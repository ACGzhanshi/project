import os
import json
import django
import uuid

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.universities.models import University, Major, AdmissionScore
from django.db import transaction
TYPE_MAP = {
    '1': '理科/物理类',
    '2': '文科/历史类',
    '3': '综合',
}


def to_int(val):
    if not val or str(val).strip() in ['-', '', 'null', 'None']: return None
    try:
        return int(float(str(val).strip()))
    except ValueError:
        return None


def parse_duration(val):
    if not val: return 4
    val_str = str(val)
    if '三' in val_str or '3' in val_str: return 3
    if '五' in val_str or '5' in val_str: return 5
    return 4


def process_school_file(file_path, school_name, province):
    """阶段一：解析并导入学校基础属性"""
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return

    # 兼容 JSON 结构（直接是字典，或者包裹在 data / records 中）
    item = data.get('data', data)
    if isinstance(item, list) and len(item) > 0:
        item = item[0]

    # 提取常见的高考数据字段
    code = item.get('school_id') or item.get('code') or ''
    city = item.get('city_name') or item.get('city') or ''
    level = item.get('level_name') or item.get('level') or ''
    type_str = item.get('type_name') or item.get('type') or ''

    # 识别 985/211/双一流
    is_985 = str(item.get('f985', '')) in ['1', '2', 'true', 'True']
    is_211 = str(item.get('f211', '')) in ['1', '2', 'true', 'True']
    is_double_first = bool(item.get('dual_class_name') or item.get('dual_class'))

    univ_qs = University.objects.filter(name=school_name)
    if univ_qs.exists():
        # 如果学校已存在，则丰满它的属性
        univ = univ_qs.first()
        univ.city = city or univ.city
        univ.level = level or univ.level
        univ.type = type_str or univ.type
        univ.is_985 = is_985 or univ.is_985
        univ.is_211 = is_211 or univ.is_211
        univ.is_double_first = is_double_first or univ.is_double_first
        # 更新数据库
        univ.save()
    else:
        # 如果是新学校，赋予临时防冲突 CODE 并创建
        safe_code = str(code) if code else "TMP_" + str(uuid.uuid4().hex)[:10]
        try:
            University.objects.create(
                name=school_name,
                province=province,
                code=safe_code,
                city=city,
                level=level,
                type=type_str,
                is_985=is_985,
                is_211=is_211,
                is_double_first=is_double_first
            )
        except Exception:
            pass

@transaction.atomic
def process_score_file(file_path, category, year, province, school_name):
    """阶段二：解析并导入专业、计划与分数线"""
    print(f"  -> 正在处理 [{category}]: {year}年 {province} - {school_name}")
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return

    records = data.get('records', [])
    if not records: return

    # 此时学校必然已经经过第一阶段的创建或完善
    univ_qs = University.objects.filter(name=school_name)
    if not univ_qs.exists(): return
    univ = univ_qs.first()

    for item in records:
        major_obj = None
        major_name = item.get('major') or item.get('sample_major')

        if major_name:
            major_defaults = {
                'code': item.get('major_code') or '',
                'category': item.get('level2_name') or '',
                'duration': parse_duration(item.get('years') or item.get('length')),
                'major_group': item.get('major_group_info') or item.get('major_group') or '',
                'tuition': str(item.get('tuition') or '')[:50]
            }
            major_defaults = {k: v for k, v in major_defaults.items() if v not in [None, '']}
            major_obj, _ = Major.objects.update_or_create(university=univ, name=major_name, defaults=major_defaults)

        min_score_val = to_int(item.get('min_score') or item.get('min'))
        if min_score_val is None:
            continue

        score_defaults = {
            'min_score': min_score_val,
            'max_score': to_int(item.get('max_score') or item.get('max')),
            'avg_score': to_int(item.get('avg_score') or item.get('average')),
            'min_rank': to_int(item.get('min_rank') or item.get('min_section')),
            'plan_count': to_int(item.get('enrollment') or item.get('plan_number') or item.get('num')),
        }
        score_defaults = {k: v for k, v in score_defaults.items() if v is not None}

        subject_type = TYPE_MAP.get(str(item.get('type')), item.get('recruit_type') or '其他')
        batch_val = item.get('batch') or item.get('local_batch_name') or '默认批次'

        AdmissionScore.objects.update_or_create(
            university=univ,
            major=major_obj,
            year=to_int(year),
            province=province,
            subject_type=subject_type,
            batch=batch_val,
            defaults=score_defaults
        )


def run_import():
    data_root = os.path.join(os.path.dirname(__file__), 'data')

    # 【第一阶段】：深度扫描学校元数据
    schools_path = os.path.join(data_root, 'schools')
    if os.path.exists(schools_path):
        print(">>> [第一阶段] 开始导入 2800+ 学校基础元数据...")
        for province in os.listdir(schools_path):
            prov_path = os.path.join(schools_path, province)
            if not os.path.isdir(prov_path): continue

            for file in os.listdir(prov_path):
                if file.endswith('.json'):
                    school_name = file.replace('.json', '')
                    file_path = os.path.join(prov_path, file)
                    process_school_file(file_path, school_name, province)

        print(">>> 学校基础数据同步完毕！")

    # 【第二阶段】：导入招生计划与历年分数
    categories = ['plans', 'school_scores', 'scores']
    print(">>> [第二阶段] 开始导入专业与历年分数线...")
    for cat in categories:
        cat_path = os.path.join(data_root, cat)
        if not os.path.exists(cat_path): continue

        for year in os.listdir(cat_path):
            year_path = os.path.join(cat_path, year)
            if not os.path.isdir(year_path): continue

            for province in os.listdir(year_path):
                prov_path = os.path.join(year_path, province)
                if not os.path.isdir(prov_path): continue

                for file in os.listdir(prov_path):
                    if file.endswith('.json'):
                        school_name = file.replace('.json', '')
                        file_path = os.path.join(prov_path, file)
                        process_score_file(file_path, cat, year, province, school_name)


if __name__ == "__main__":
    run_import()
    print(">>> [大功告成] 所有学校、专业、分数数据已彻底融合并入库！")