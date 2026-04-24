"""推荐引擎，基于历年分数线和录取概率计算"""
import json
import random
import requests
from django.conf import settings
from django.db.models import Avg, Min, Q
from apps.universities.models import University, Major, AdmissionScore


def calculate_probability(user_score, ref_score):
    """优化后的概率算法：扩大低分段覆盖面"""
    diff = user_score - ref_score
    if diff >= 25: return min(98.0, 85 + diff * 0.4)
    if diff >= 0: return 50 + diff * 1.4  # 分数持平即有 50% 概率，属于“稳”
    if diff >= -20: return 20 + (diff + 20) * 1.5 # 分差在 -20 内都有机会“冲”
    return max(2.0, 10 + diff * 0.5)


def get_recommendations(score, province, subject_type, subjects='', interest_majors=''):
    """获取冲稳保推荐院校 """
    clean_province = province.replace('省', '').replace('市', '').replace('自治区', '').replace('壮族', '')

    # 1. 放弃精确匹配，直接开启“字眼核爆搜索”
    subj_q = Q()
    if '理' in subject_type or '物' in subject_type:
        subj_q = Q(subject_type__icontains='理') | Q(subject_type__icontains='物') | Q(subject_type__icontains='理工')
    elif '文' in subject_type or '史' in subject_type:
        subj_q = Q(subject_type__icontains='文') | Q(subject_type__icontains='史') | Q(subject_type__icontains='文史')
    else:
        subj_q = Q(subject_type__icontains=subject_type)

    # 2. 移除 min_score 限制，防止因数据类型异常导致过滤
    recent_scores = AdmissionScore.objects.filter(
        Q(province__icontains=clean_province),
        subj_q,
        year__gte=2022
    ).values('university_id').annotate(
        avg_min=Avg('min_score'),
        absolute_min=Min('min_score')
    )

    # 3. 🚨 独家诊断拦截器：让数据库自己开口说话！
    if not recent_scores.exists():
        sample = AdmissionScore.objects.filter(province__icontains=clean_province).first()
        if sample:
            error_msg = (
                f"【拦截诊断】查到了 {clean_province} 的数据，但科类对不上！\n"
                f"你选的是：'{subject_type}'\n"
                f"但数据库里这条数据的 科类 竟然写的是：'{sample.subject_type}'！"
            )
            raise ValueError(error_msg)
        else:
            raise ValueError(
                f"【拦截诊断】连一条 {clean_province} 的数据都没查到！请确认表里的省份列是不是存成了拼音或地区代码。")

    rush_list = []
    stable_list = []
    safe_list = []

    for item in recent_scores:
        ref_score = (float(item['avg_min']) * 0.7) + (float(item['absolute_min']) * 0.3)
        prob = calculate_probability(score, ref_score)

        try:
            uni = University.objects.get(id=item['university_id'])
        except University.DoesNotExist:
            continue

        rec = {
            'university_id': uni.id,
            'university_name': uni.name,
            'province': uni.province,
            'level': uni.level,
            'is_985': uni.is_985,
            'is_211': uni.is_211,
            'avg_min_score': int(item['avg_min']),
            'probability': round(prob, 1),
            'employment_rate': float(uni.employment_rate) if uni.employment_rate else None,
        }

        # ================== 修复后的真实专业推荐逻辑 ==================
        # 复用上面的 clean_province 和 subj_q，确保专业分数的查询同样具备超强兼容性
        valid_major_scores = AdmissionScore.objects.filter(
            Q(province__icontains=clean_province),
            subj_q,
            university=uni,
            year__gte=2022,
            major__isnull=False
        ).values('major_id').annotate(
            major_avg_min=Avg('min_score')
        )  # 🚨 删除了这里原本的 .order_by('-major_avg_min')[:5]

        major_list = []

        if valid_major_scores:
            # 1. 遍历该校所有的专业，计算每一个的录取概率
            for m_item in valid_major_scores:
                try:
                    m = Major.objects.get(id=m_item['major_id'])
                    m_prob = calculate_probability(score, float(m_item['major_avg_min']))

                    major_list.append({
                        'major_id': m.id,
                        'major_name': m.name,
                        'category': m.category,
                        'employment_rate': float(m.employment_rate) if m.employment_rate else None,
                        'avg_salary': m.avg_salary,
                        # 🚨 核心修改 1：提取并透传学科评估等级
                        'discipline_eval': m.discipline_eval or '',
                        'probability': round(m_prob, 1),
                        'real_min_score': int(m_item['major_avg_min'])
                    })
                except Major.DoesNotExist:
                    continue

            # 2. 🚨 核心修复：在内存中按“录取概率”从高到低排序，只取前 5 个最稳的专业！
            major_list.sort(key=lambda x: x['probability'], reverse=True)
            major_list = major_list[:5]

        else:
            # 兜底方案
            uni_majors = Major.objects.filter(university=uni).order_by('-employment_rate')[:5]
            for m in uni_majors:
                major_list.append({
                    'major_id': m.id,
                    'major_name': f"{m.name} (本省暂无专业录取数据)",
                    'category': m.category,
                    'employment_rate': float(m.employment_rate) if m.employment_rate else None,
                    'avg_salary': m.avg_salary,
                    # 🚨 核心修改 2：兜底方案中也需透传学科评估等级
                    'discipline_eval': m.discipline_eval or '',
                    'probability': 0,
                })

        rec['majors'] = major_list
        # ==============================================================

        if 15 <= prob < 45:
            rec['level'] = 'rush'
            rush_list.append(rec)
        elif 45 <= prob < 80:
            rec['level'] = 'stable'
            stable_list.append(rec)
        elif prob >= 80:
            rec['level'] = 'safe'
            safe_list.append(rec)

    rush_list.sort(key=lambda x: x['probability'], reverse=True)
    stable_list.sort(key=lambda x: x['probability'], reverse=True)
    safe_list.sort(key=lambda x: x['probability'], reverse=True)

    return {
        'rush': rush_list[:10],
        'stable': stable_list[:10],
        'safe': safe_list[:10],
    }


def qianwen_analyze(score, province, recommendations, assessment_data=None):
    """调用千问API进行智能分析（已融合专业测评结果）"""
    try:
        assessment_text = ""
        if assessment_data:
            top_dim = assessment_data.get('top_dimension', '未知')
            majors = assessment_data.get('recommended_majors', '无特定推荐')
            assessment_text = f"\n该学生的专业倾向测评结果如下：\n核心优势维度：{top_dim}\n系统倾向推荐的专业：{majors}\n"

        prompt = f"""你是一位资深的高考志愿填报专家。
学生信息：高考分数{score}分，{province}考生。{assessment_text}

系统基于分数推荐了以下院校：
冲刺院校：{json.dumps([r['university_name'] for r in recommendations.get('rush', [])[:5]], ensure_ascii=False)}
稳妥院校：{json.dumps([r['university_name'] for r in recommendations.get('stable', [])[:5]], ensure_ascii=False)}
保底院校：{json.dumps([r['university_name'] for r in recommendations.get('safe', [])[:5]], ensure_ascii=False)}

请结合学生的【分数情况】以及【专业倾向测评结果】（如果有），给出专业的志愿填报建议，包括：
1. 对推荐方案的整体评价（结合分数和性格特点是否匹配）
2. 填报策略建议（重点建议他们应该关注哪些推荐院校里的哪些专业）
3. 需要注意的风险点
请用简洁、专业且富有同理心的语言回答。"""

        headers = {
            'Authorization': f'Bearer {settings.QIANWEN_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': settings.QIANWEN_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        resp = requests.post(settings.QIANWEN_API_URL, headers=headers, json=data, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            return result['choices'][0]['message']['content']
        return '智能分析暂时不可用，请稍后再试。'
    except Exception as e:
        return f'智能分析服务异常：{str(e)}'