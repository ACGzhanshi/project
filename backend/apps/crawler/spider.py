"""爬虫引擎 - 从掌上高考(zjzw.cn)爬取真实高考数据并写入数据库"""
import json
import random
import time
import requests
from datetime import datetime
from .models import CrawlerTask, CrawlerData


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
}

BASE_API = 'https://api.zjzw.cn/web/api/'


def _append_log(task, log_lines, msg):
    """追加日志并保存"""
    log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    task.log = '\n'.join(log_lines)
    task.save()


def crawl_universities(task):
    """从掌上高考爬取真实院校数据并写入数据库"""
    from apps.universities.models import University

    task.status = 'running'
    task.started_at = datetime.now()
    task.log = ''
    task.success_count = 0
    task.fail_count = 0
    task.total_count = 0
    task.save()

    log_lines = []
    log = lambda msg: _append_log(task, log_lines, msg)

    log('开始从掌上高考爬取院校数据...')
    log(f'数据源: api.zjzw.cn (掌上高考)')

    all_schools = []
    page = 1
    page_size = 30

    while True:
        try:
            url = (f'{BASE_API}?keyword=&page={page}&province_id=&ranktype=&'
                   f'request_type=1&size={page_size}&type=&'
                   f'uri=apidata/api/gk/school/lists')
            log(f'正在请求第{page}页 (每页{page_size}条)...')
            resp = requests.get(url, headers=HEADERS, timeout=15)

            if resp.status_code != 200:
                log(f'请求失败，HTTP {resp.status_code}')
                break

            data = resp.json()
            if data.get('code') != '0000':
                log(f'API返回错误: {data.get("message", "未知")}')
                break

            items = data.get('data', {}).get('item', [])
            total_found = data.get('data', {}).get('numFound', 0)

            if not items:
                log(f'第{page}页无数据，爬取结束')
                break

            for item in items:
                school = {
                    'school_id': item.get('school_id'),
                    'name': item.get('name', ''),
                    'code': str(item.get('code_enroll', '')),
                    'province': item.get('province_name', ''),
                    'city': item.get('city_name', ''),
                    'level': item.get('level_name', '本科'),
                    'type': item.get('type_name', '综合').replace('类', ''),
                    'is_985': item.get('f985') in ('1', 1, True),
                    'is_211': item.get('f211') in ('1', 1, True),
                    'is_double_first': bool(item.get('dual_class')),
                    'nature': item.get('nature_name', ''),
                    'belong': item.get('belong', ''),
                }
                if school['name']:
                    all_schools.append(school)

            log(f'第{page}页获取 {len(items)} 所院校 (累计 {len(all_schools)}/{total_found})')


            if page >= 100 or len(all_schools) >= total_found:
                break

            page += 1
            time.sleep(random.uniform(0.8, 1.5))

        except Exception as e:
            log(f'第{page}页请求异常: {str(e)[:100]}')
            break

    if not all_schools:
        log('未获取到任何数据，任务失败')
        task.status = 'failed'
        task.finished_at = datetime.now()
        task.save()
        return task

    task.total_count = len(all_schools)
    log(f'共爬取到 {len(all_schools)} 所院校，开始写入数据库...')

    for i, school in enumerate(all_schools):
        try:
            CrawlerData.objects.create(
                task=task, data_type='university',
                raw_data=school, is_cleaned=True, cleaned_data=school
            )
            University.objects.update_or_create(
                code=school['code'],
                defaults={
                    'name': school['name'],
                    'province': school.get('province', ''),
                    'city': school.get('city', ''),
                    'level': school.get('level', '本科'),
                    'type': school.get('type', '综合'),
                    'is_985': school.get('is_985', False),
                    'is_211': school.get('is_211', False),
                    'is_double_first': school.get('is_double_first', False),
                }
            )
            task.success_count = i + 1
            if (i + 1) % 20 == 0:
                log(f'已写入 {i + 1}/{len(all_schools)} 所院校')
                task.save()
        except Exception as e:
            task.fail_count += 1
            log(f'写入 {school.get("name", "?")} 失败: {str(e)[:60]}')

    task.status = 'success'
    task.finished_at = datetime.now()
    log(f'院校爬取完成！成功 {task.success_count} 所，失败 {task.fail_count} 所')
    task.save()
    return task


def crawl_scores(task):
    """从掌上高考爬取真实录取分数线并写入数据库"""
    from apps.universities.models import University, AdmissionScore

    task.status = 'running'
    task.started_at = datetime.now()
    task.log = ''
    task.success_count = 0
    task.fail_count = 0
    task.total_count = 0
    task.save()

    log_lines = []
    log = lambda msg: _append_log(task, log_lines, msg)

    log('开始从掌上高考爬取录取分数线...')
    log(f'数据源: api.zjzw.cn (掌上高考)')

    # 获取有school_id的院校，优先爬排名靠前的
    universities = University.objects.all().order_by('ranking', 'id')[:30]
    if not universities.exists():
        log('数据库中无院校数据，请先执行院校信息采集')
        task.status = 'failed'
        task.finished_at = datetime.now()
        task.save()
        return task

    log(f'将为 {universities.count()} 所院校爬取分数线')

    # 先通过院校列表API获取school_id映射
    school_id_map = {}
    log('正在获取院校ID映射...')
    for uni in universities:
        try:
            url = f'{BASE_API}?keyword={uni.name}&page=1&size=3&uri=apidata/api/gk/school/lists'
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                items = resp.json().get('data', {}).get('item', [])
                for item in items:
                    if item.get('name') == uni.name:
                        school_id_map[uni.id] = item.get('school_id')
                        break
            time.sleep(random.uniform(0.3, 0.8))
        except:
            pass
    log(f'获取到 {len(school_id_map)} 所院校的ID映射')

    total = 0
    success = 0

    for uni in universities:
        sid = school_id_map.get(uni.id)
        if not sid:
            log(f'跳过 {uni.name}（未找到school_id）')
            continue

        log(f'正在爬取 {uni.name} (school_id={sid}) 的分数线...')

        try:
            url = f'{BASE_API}?school_id={sid}&uri=apidata/api/gk/score/province'
            resp = requests.get(url, headers=HEADERS, timeout=15)

            if resp.status_code != 200:
                log(f'  请求失败 HTTP {resp.status_code}')
                continue

            data = resp.json()
            items = data.get('data', {}).get('item', [])

            if not items:
                log(f'  {uni.name} 无分数线数据')
                continue

            count = 0
            for item in items:
                min_score = item.get('min')
                year = item.get('year')
                if not min_score or not year:
                    continue
                # min可能是字符串"-"
                try:
                    min_score = int(min_score)
                except (ValueError, TypeError):
                    continue

                score_data = {
                    'year': int(year),
                    'province': item.get('local_province_name', ''),
                    'subject_type': item.get('local_type_name', item.get('zslx_name', '综合')),
                    'batch': item.get('local_batch_name', '本科批'),
                    'min_score': min_score,
                    'max_score': _safe_int(item.get('max')),
                    'avg_score': _safe_int(item.get('average')),
                    'min_rank': _safe_int(item.get('min_section')),
                }

                total += 1
                try:
                    CrawlerData.objects.create(
                        task=task, data_type='score',
                        raw_data={**score_data, 'university': uni.name},
                        is_cleaned=True, cleaned_data=score_data
                    )
                    AdmissionScore.objects.update_or_create(
                        university=uni,
                        year=score_data['year'],
                        province=score_data['province'],
                        subject_type=score_data['subject_type'],
                        batch=score_data['batch'],
                        defaults={
                            'min_score': score_data['min_score'],
                            'max_score': score_data.get('max_score'),
                            'avg_score': score_data.get('avg_score'),
                            'min_rank': score_data.get('min_rank'),
                        }
                    )
                    success += 1
                    count += 1
                except Exception as e:
                    task.fail_count += 1

            task.success_count = success
            task.total_count = total
            task.save()
            log(f'  {uni.name} 写入 {count} 条分数线')

        except Exception as e:
            log(f'  {uni.name} 爬取异常: {str(e)[:80]}')

        time.sleep(random.uniform(0.8, 1.5))

    task.status = 'success'
    task.finished_at = datetime.now()
    log(f'分数线爬取完成！共 {total} 条，成功 {success} 条，失败 {task.fail_count} 条')
    task.save()
    return task


def _safe_int(val):
    """安全转换为int，失败返回None"""
    if val is None or val == '-' or val == '':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


# 兼容旧函数名
simulate_crawl_universities = crawl_universities
simulate_crawl_scores = crawl_scores
