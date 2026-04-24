# backend/generate_cf_data.py
import random
import pandas as pd
import os


def generate_fake_ratings(num_users=1000):
    """生成带有群体特征的假评分数据"""
    # 假设我们有 30 个专业 (ID 1 到 30)
    stem_majors = list(range(1, 11))  # 理工类专业 (1-10)
    arts_majors = list(range(11, 21))  # 文史类专业 (11-20)
    biz_majors = list(range(21, 31))  # 经管类专业 (21-30)

    data = []

    for user_id in range(1, num_users + 1):
        # 随机决定这个用户的偏好阵营
        user_preference = random.choice(['stem', 'arts', 'biz'])

        # 决定该用户评了几个专业的星（每个用户随机评价 5-10 个专业）
        num_ratings = random.randint(5, 10)

        # 挑出该用户评价的专业
        rated_majors = random.sample(range(1, 31), num_ratings)

        for major_id in rated_majors:
            # 核心逻辑：如果专业符合用户偏好，大概率给高分（4-5分）；否则给低分（1-3分）
            if (user_preference == 'stem' and major_id in stem_majors) or \
                    (user_preference == 'arts' and major_id in arts_majors) or \
                    (user_preference == 'biz' and major_id in biz_majors):
                rating = random.choices([4, 5], weights=[0.4, 0.6])[0]
            else:
                rating = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]

            data.append({
                'user_id': user_id,
                'major_id': major_id,
                'rating': rating
            })

    df = pd.DataFrame(data)

    # 确保 data 目录存在
    os.makedirs('data', exist_ok=True)
    csv_path = 'data/fake_user_ratings.csv'
    df.to_csv(csv_path, index=False)
    print(f"成功生成 {len(df)} 条协同过滤训练数据！已保存至 {csv_path}")


if __name__ == '__main__':
    generate_fake_ratings()