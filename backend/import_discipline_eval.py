import os
import sys
import django
import pandas as pd
from collections import Counter

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.universities.models import University, Major
from django.db.models import Q


def run_import():
    excel_path = 'data/教育部第四次全国高校学科评估(2017.12.28).xlsx'

    if not os.path.exists(excel_path):
        print(f"找不到文件: {excel_path}，请检查路径。")
        return

    print("正在读取教育部学科评估数据 (解析中)...")

    try:
        df = pd.read_excel(excel_path, header=1)
    except Exception as e:
        print(f"读取 Excel 失败: {e}")
        return

    success_count = 0
    not_found_unis = set()

    # 🚀 新增：用于详细统计各个等级到底导入了多少个专业
    tag_counter = Counter()

    def get_search_keys(discipline):
        base = discipline.replace('科学与技术', '').replace('工程', '').replace('学', '')
        keys = [base]
        if '与' in base:
            keys.extend(base.split('与'))
        return [k for k in keys if len(k) >= 2]

    for index, row in df.iterrows():
        uni_name = str(row.get('院校名称', '')).strip()
        discipline_name = str(row.get('一级学科名称', '')).strip()
        eval_result = str(row.get('评估结果', '')).strip()

        if not uni_name or uni_name == 'nan' or not discipline_name or not eval_result:
            continue

        try:
            university = University.objects.filter(name__icontains=uni_name).first()
            if not university:
                not_found_unis.add(uni_name)
                continue

            search_keys = get_search_keys(discipline_name)
            if not search_keys:
                continue

            query = Q()
            for key in search_keys:
                query |= Q(name__icontains=key)

            majors_to_update = Major.objects.filter(university=university).filter(query)

            for major in majors_to_update:
                major.discipline_eval = eval_result
                major.save()

                success_count += 1
                # 🚀 记录该等级的数量
                tag_counter[eval_result] += 1

        except Exception as e:
            pass

    print(f"\n🎉 导入完成！总共为 {success_count} 个本科专业打上了官方评估标签。")
    print("-" * 30)
    print("🏆 标签详细分布统计：")

    # 按 A+, A, A-, B+... 的顺序打印统计结果
    for tag, count in tag_counter.most_common():
        print(f"  [{tag}] 级: {count} 个专业")
    print("-" * 30)

    if not_found_unis:
        print(
            f"\n⚠️ 以下院校因近年来改名或合并，在数据库中未匹配到，已跳过 ({len(not_found_unis)}所): \n{', '.join(list(not_found_unis)[:15])} 等...")


if __name__ == '__main__':
    run_import()