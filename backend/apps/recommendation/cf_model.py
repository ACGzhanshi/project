# backend/apps/recommendation/cf_model.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

# 全局缓存模型，避免每次请求都重新计算
_item_similarity_df = None


def train_cf_model():
    """训练协同过滤模型（这里其实是计算余弦相似度矩阵）"""
    global _item_similarity_df

    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data',
                            'fake_user_ratings.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError("未找到训练数据，请先运行 generate_cf_data.py")

    print("正在加载数据并训练协同过滤模型...")
    df = pd.read_csv(csv_path)

    # 构建 用户-专业 评分矩阵
    # 行是 user_id，列是 major_id，值是 rating，没评过分的填 0
    user_item_matrix = df.pivot_table(index='user_id', columns='major_id', values='rating').fillna(0)

    # 计算专业之间的余弦相似度 (Cosine Similarity)
    # 转置矩阵 (T) 是因为我们要算专业和专业的相似度，而不是用户和用户
    item_sim_matrix = cosine_similarity(user_item_matrix.T)

    # 转成 DataFrame 方便后续通过专业 ID 检索
    _item_similarity_df = pd.DataFrame(
        item_sim_matrix,
        index=user_item_matrix.columns,
        columns=user_item_matrix.columns
    )
    print("模型训练完成！相似度矩阵已就绪。")


def get_cf_recommendations(target_major_id, top_n=5):
    """
    传入一个专业ID，返回协同过滤算法推荐的相似专业列表。
    """
    global _item_similarity_df
    if _item_similarity_df is None:
        train_cf_model()

    if target_major_id not in _item_similarity_df.index:
        return []  # 如果输入了一个不存在的专业，返回空

    # 获取该专业与其他所有专业的相似度，降序排列
    similar_scores = _item_similarity_df[target_major_id].sort_values(ascending=False)

    # 排除它自己 (相似度必定是1.0)，然后取前 N 个
    similar_scores = similar_scores.drop(target_major_id).head(top_n)

    # 返回推荐的专业 ID 和相似度得分
    recommendations = []
    for major_id, score in similar_scores.items():
        recommendations.append({
            'major_id': major_id,
            'sim_score': round(score, 4)  # 保留4位小数展示
        })

    return recommendations