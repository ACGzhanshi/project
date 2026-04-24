import os
import json
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.universities.models import StandardMajor


def import_standard_majors(json_path):
    print(f"准备读取标准专业库: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # 根据你上传的 JSON 结构，数据在 "data" 列表中
    records = content.get('data', [])
    if not records:
        print("JSON 文件中没有找到 data 数组")
        return

    print(f"共发现 {len(records)} 个标准专业，开始导入...")

    count = 0
    for item in records:
        special_id = item.get('special_id')
        if not special_id:
            continue

        def parse_int(val):
            if not val or str(val).strip() == '': return None
            try:
                return int(float(str(val).strip()))
            except ValueError:
                return None

        # 清洗男女比例（去掉%号或直接存数字）
        boy_rate = item.get('boy_rate', '')
        girl_rate = item.get('girl_rate', '')

        StandardMajor.objects.update_or_create(
            special_id=str(special_id),
            defaults={
                'code': item.get('code', ''),
                'name': item.get('name', ''),
                'level1_name': item.get('level1_name', ''),
                'level2_name': item.get('level2_name', ''),
                'level3_name': item.get('level3_name', ''),
                'degree': item.get('degree', ''),
                'years': item.get('years', ''),
                'salary_avg': parse_int(item.get('salary_avg')),
                'salary_5year': parse_int(item.get('salary_5year')),
                'boy_rate': parse_int(boy_rate),
                'girl_rate': parse_int(girl_rate),
            }
        )
        count += 1

    print(f"导入完成！成功更新/新增了 {count} 个标准专业记录。")


if __name__ == "__main__":
    # 指向你的 majors.json 文件的实际路径
    # 假设你把它放在了 backend/data/ 目录下
    target_json = os.path.join(os.path.dirname(__file__), 'data', 'majors.json')

    if os.path.exists(target_json):
        import_standard_majors(target_json)
    else:
        print(f"找不到文件: {target_json}，请检查路径。")