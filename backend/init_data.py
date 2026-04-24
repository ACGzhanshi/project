"""初始化演示数据脚本"""
import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.hashers import make_password
from apps.users.models import User
from apps.universities.models import University, Major, AdmissionScore, EnrollmentPlan
from apps.recommendation.models import AssessmentQuestion, RecommendRecord, AssessmentResult
from apps.volunteer.models import VolunteerForm, VolunteerItem
from apps.crawler.models import CrawlerTask, CrawlerData
from apps.system.models import (
    OperationLog, DataPermission, SystemConfig, ModelTrainLog
)

def create_users():
    """创建演示用户"""
    print("创建用户...")
    users_data = [
        {'username': 'student1', 'role': 'student', 'phone': '13800001001',
         'province': '广东', 'score': 620, 'subject_type': '物理类',
         'subjects': '物理,化学,生物'},
        {'username': 'student2', 'role': 'student', 'phone': '13800001002',
         'province': '北京', 'score': 580, 'subject_type': '物理类',
         'subjects': '物理,化学,地理'},
        {'username': 'student3', 'role': 'student', 'phone': '13800001003',
         'province': '浙江', 'score': 650, 'subject_type': '物理类',
         'subjects': '物理,生物,政治'},
        {'username': 'teacher1', 'role': 'teacher', 'phone': '13800002001',
         'province': '广东'},
        {'username': 'parent1', 'role': 'parent', 'phone': '13800003001',
         'province': '北京'},
        {'username': 'dataadmin', 'role': 'data_admin', 'phone': '13800004001'},
        {'username': 'sysadmin', 'role': 'sys_admin', 'phone': '13800005001'},
    ]
    for u in users_data:
        if not User.objects.filter(username=u['username']).exists():
            User.objects.create(
                username=u['username'],
                password=make_password('123456'),
                role=u.get('role', 'student'),
                phone=u.get('phone', ''),
                province=u.get('province', ''),
                score=u.get('score'),
                subject_type=u.get('subject_type', ''),
                subjects=u.get('subjects', ''),
                is_active=True,
            )
    print(f"  已创建 {len(users_data)} 个用户")


def create_universities():
    """创建院校数据"""
    print("创建院校数据...")
    unis = [
        {'name': '北京大学', 'code': '10001', 'province': '北京', 'city': '北京',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 1, 'employment_rate': 98.5,
         'description': '北京大学创办于1898年，是中国第一所国立综合性大学'},
        {'name': '清华大学', 'code': '10003', 'province': '北京', 'city': '北京',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 2, 'employment_rate': 98.8,
         'description': '清华大学是中国著名高等学府，坐落于北京西北郊'},
        {'name': '复旦大学', 'code': '10246', 'province': '上海', 'city': '上海',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 3, 'employment_rate': 97.2,
         'description': '复旦大学是中国人自主创办的第一所高等院校'},
        {'name': '浙江大学', 'code': '10335', 'province': '浙江', 'city': '杭州',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 4, 'employment_rate': 97.5,
         'description': '浙江大学是一所历史悠久、声誉卓著的高等学府'},
        {'name': '上海交通大学', 'code': '10248', 'province': '上海', 'city': '上海',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 5, 'employment_rate': 97.8,
         'description': '上海交通大学是我国历史最悠久的高等学府之一'},
        {'name': '南京大学', 'code': '10284', 'province': '江苏', 'city': '南京',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 6, 'employment_rate': 96.8,
         'description': '南京大学是一所历史悠久、声誉卓著的百年名校'},
        {'name': '中国科学技术大学', 'code': '10358', 'province': '安徽', 'city': '合肥',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 7, 'employment_rate': 97.0,
         'description': '中国科学技术大学是中国科学院直属的全国重点大学'},
        {'name': '华中科技大学', 'code': '10487', 'province': '湖北', 'city': '武汉',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 8, 'employment_rate': 96.5,
         'description': '华中科技大学是国家教育部直属重点综合性大学'},
        {'name': '武汉大学', 'code': '10486', 'province': '湖北', 'city': '武汉',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 9, 'employment_rate': 96.2,
         'description': '武汉大学是国家教育部直属重点综合性大学'},
        {'name': '中山大学', 'code': '10558', 'province': '广东', 'city': '广州',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 10, 'employment_rate': 96.0,
         'description': '中山大学由孙中山先生创办，有着一百多年办学传统'},
        {'name': '四川大学', 'code': '10610', 'province': '四川', 'city': '成都',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 11, 'employment_rate': 95.5,
         'description': '四川大学是教育部直属全国重点大学'},
        {'name': '西安交通大学', 'code': '10698', 'province': '陕西', 'city': '西安',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 12, 'employment_rate': 96.3,
         'description': '西安交通大学是我国最早兴办的高等学府之一'},
        {'name': '哈尔滨工业大学', 'code': '10213', 'province': '黑龙江', 'city': '哈尔滨',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 13, 'employment_rate': 96.8,
         'description': '哈尔滨工业大学始建于1920年'},
        {'name': '同济大学', 'code': '10247', 'province': '上海', 'city': '上海',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 14, 'employment_rate': 96.5,
         'description': '同济大学历史悠久、声誉卓著'},
        {'name': '北京师范大学', 'code': '10027', 'province': '北京', 'city': '北京',
         'level': '本科', 'type': '师范', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 15, 'employment_rate': 95.8,
         'description': '北京师范大学是教育部直属重点大学'},
        {'name': '东南大学', 'code': '10286', 'province': '江苏', 'city': '南京',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 16, 'employment_rate': 96.0,
         'description': '东南大学是中央直管、教育部直属的全国重点大学'},
        {'name': '厦门大学', 'code': '10384', 'province': '福建', 'city': '厦门',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 17, 'employment_rate': 95.5,
         'description': '厦门大学由著名爱国华侨领袖陈嘉庚先生于1921年创办'},
        {'name': '天津大学', 'code': '10056', 'province': '天津', 'city': '天津',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 18, 'employment_rate': 95.8,
         'description': '天津大学是教育部直属国家重点大学'},
        {'name': '华南理工大学', 'code': '10561', 'province': '广东', 'city': '广州',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 19, 'employment_rate': 96.2,
         'description': '华南理工大学地处广州，是直属教育部的全国重点大学'},
        {'name': '山东大学', 'code': '10422', 'province': '山东', 'city': '济南',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 20, 'employment_rate': 95.0,
         'description': '山东大学是一所历史悠久、学科齐全的综合性大学'},
        {'name': '北京航空航天大学', 'code': '10006', 'province': '北京', 'city': '北京',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 21, 'employment_rate': 97.0,
         'description': '北京航空航天大学是新中国第一所航空航天高等学府'},
        {'name': '大连理工大学', 'code': '10141', 'province': '辽宁', 'city': '大连',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 22, 'employment_rate': 95.5,
         'description': '大连理工大学是教育部直属全国重点大学'},
        {'name': '吉林大学', 'code': '10183', 'province': '吉林', 'city': '长春',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 23, 'employment_rate': 94.8,
         'description': '吉林大学是教育部直属的全国重点综合性大学'},
        {'name': '电子科技大学', 'code': '10614', 'province': '四川', 'city': '成都',
         'level': '本科', 'type': '理工', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 24, 'employment_rate': 96.8,
         'description': '电子科技大学坐落于四川省成都市'},
        {'name': '中南大学', 'code': '10533', 'province': '湖南', 'city': '长沙',
         'level': '本科', 'type': '综合', 'is_985': True, 'is_211': True,
         'is_double_first': True, 'ranking': 25, 'employment_rate': 95.5,
         'description': '中南大学坐落在中国历史文化名城长沙'},
    ]
    for u in unis:
        if not University.objects.filter(code=u['code']).exists():
            University.objects.create(**u)
    print(f"  已创建 {len(unis)} 所院校")


def create_majors():
    """创建专业数据"""
    print("创建专业数据...")
    major_templates = [
        {'name': '计算机科学与技术', 'code': '080901', 'category': '工学', 'duration': 4,
         'degree': '工学学士', 'employment_rate': 96.5, 'avg_salary': 12000,
         'description': '培养具有良好科学素养的计算机专业高级人才'},
        {'name': '软件工程', 'code': '080902', 'category': '工学', 'duration': 4,
         'degree': '工学学士', 'employment_rate': 95.8, 'avg_salary': 11500,
         'description': '培养具有软件开发和项目管理能力的高级人才'},
        {'name': '人工智能', 'code': '080717', 'category': '工学', 'duration': 4,
         'degree': '工学学士', 'employment_rate': 97.0, 'avg_salary': 13000,
         'description': '培养人工智能领域的创新型人才'},
        {'name': '电子信息工程', 'code': '080701', 'category': '工学', 'duration': 4,
         'degree': '工学学士', 'employment_rate': 94.5, 'avg_salary': 10000,
         'description': '培养电子信息领域的工程技术人才'},
        {'name': '金融学', 'code': '020301', 'category': '经济学', 'duration': 4,
         'degree': '经济学学士', 'employment_rate': 93.0, 'avg_salary': 10500,
         'description': '培养具有金融理论和实务能力的专门人才'},
        {'name': '临床医学', 'code': '100201', 'category': '医学', 'duration': 5,
         'degree': '医学学士', 'employment_rate': 92.0, 'avg_salary': 8500,
         'description': '培养具有临床医学基本理论和技能的医学人才'},
        {'name': '法学', 'code': '030101', 'category': '法学', 'duration': 4,
         'degree': '法学学士', 'employment_rate': 88.5, 'avg_salary': 9000,
         'description': '培养系统掌握法学知识的法律专门人才'},
        {'name': '工商管理', 'code': '120201', 'category': '管理学', 'duration': 4,
         'degree': '管理学学士', 'employment_rate': 90.0, 'avg_salary': 9500,
         'description': '培养具有管理、经济、法律等方面知识的高级人才'},
        {'name': '汉语言文学', 'code': '050101', 'category': '文学', 'duration': 4,
         'degree': '文学学士', 'employment_rate': 85.0, 'avg_salary': 7500,
         'description': '培养具有汉语言文学基本理论和知识的人才'},
        {'name': '数学与应用数学', 'code': '070101', 'category': '理学', 'duration': 4,
         'degree': '理学学士', 'employment_rate': 91.0, 'avg_salary': 9000,
         'description': '培养掌握数学科学基本理论与方法的专门人才'},
    ]
    universities = University.objects.all()
    count = 0
    for uni in universities:
        selected = random.sample(major_templates, min(len(major_templates), random.randint(5, 8)))
        for m in selected:
            if not Major.objects.filter(university=uni, code=m['code']).exists():
                Major.objects.create(university=uni, **m)
                count += 1
    print(f"  已创建 {count} 个专业")


def create_admission_scores():
    """创建录取分数线数据"""
    print("创建录取分数线...")
    provinces = ['北京', '上海', '广东', '浙江', '江苏', '山东', '河南', '四川', '湖北', '湖南']
    universities = University.objects.all()
    count = 0
    for uni in universities:
        base = 700 - uni.ranking * 8 + random.randint(-10, 10)
        for year in [2022, 2023, 2024]:
            for province in provinces:
                year_adj = (year - 2022) * random.randint(-3, 5)
                prov_adj = random.randint(-15, 15)
                min_score = max(400, min(700, base + year_adj + prov_adj))
                for st in ['物理类', '历史类']:
                    st_adj = -20 if st == '历史类' else 0
                    final_min = min_score + st_adj
                    if not AdmissionScore.objects.filter(
                        university=uni, year=year, province=province, subject_type=st
                    ).exists():
                        AdmissionScore.objects.create(
                            university=uni, year=year, province=province,
                            subject_type=st, batch='本科一批',
                            min_score=final_min,
                            max_score=final_min + random.randint(10, 35),
                            avg_score=final_min + random.randint(5, 20),
                            min_rank=random.randint(100, 60000),
                            plan_count=random.randint(5, 50),
                            actual_count=random.randint(5, 50),
                        )
                        count += 1
    print(f"  已创建 {count} 条分数线数据")


def create_enrollment_plans():
    """创建招生计划"""
    print("创建招生计划...")
    provinces = ['北京', '上海', '广东', '浙江', '江苏', '山东']
    count = 0
    for uni in University.objects.all():
        majors = list(uni.majors.all())
        if not majors:
            continue
        for province in random.sample(provinces, 3):
            for major in random.sample(majors, min(3, len(majors))):
                if not EnrollmentPlan.objects.filter(
                    university=uni, major=major, year=2025, province=province
                ).exists():
                    EnrollmentPlan.objects.create(
                        university=uni, major=major, year=2025,
                        province=province, subject_type='物理类',
                        plan_count=random.randint(2, 30),
                        tuition=random.choice([5000, 5500, 6000, 8000, 10000]),
                    )
                    count += 1
    print(f"  已创建 {count} 条招生计划")


def create_assessment_questions():
    """创建测评题目"""
    print("创建测评题目...")
    questions = [
        {'content': '面对一个复杂的数学问题，你会？', 'category': '逻辑思维',
         'option_a': '兴奋地尝试各种解法', 'option_b': '按部就班地分析',
         'option_c': '寻求他人帮助', 'option_d': '换个简单的问题做'},
        {'content': '你更喜欢哪种课外活动？', 'category': '艺术创造',
         'option_a': '编程竞赛', 'option_b': '绘画或音乐',
         'option_c': '辩论赛', 'option_d': '志愿服务'},
        {'content': '你理想的工作环境是？', 'category': '商业管理',
         'option_a': '安静的实验室', 'option_b': '热闹的办公室',
         'option_c': '自由的户外', 'option_d': '严谨的医院'},
        {'content': '遇到团队分歧时，你通常会？', 'category': '社会服务',
         'option_a': '用数据说服大家', 'option_b': '倾听各方意见后协调',
         'option_c': '坚持自己的观点', 'option_d': '服从多数人的决定'},
        {'content': '你对以下哪个话题最感兴趣？', 'category': '自然探索',
         'option_a': '人工智能的未来', 'option_b': '全球气候变化',
         'option_c': '经济发展趋势', 'option_d': '文学艺术鉴赏'},
        {'content': '你更擅长哪种表达方式？', 'category': '语言表达',
         'option_a': '写代码', 'option_b': '写文章',
         'option_c': '做演讲', 'option_d': '画图表'},
        {'content': '假期你最想做什么？', 'category': '自然探索',
         'option_a': '学习新技能', 'option_b': '旅行探索',
         'option_c': '社交聚会', 'option_d': '阅读思考'},
        {'content': '你认为最重要的能力是？', 'category': '逻辑思维',
         'option_a': '逻辑分析能力', 'option_b': '沟通表达能力',
         'option_c': '创新创造能力', 'option_d': '组织管理能力'},
        {'content': '你更喜欢哪类书籍？', 'category': '语言表达',
         'option_a': '科技类', 'option_b': '文学类',
         'option_c': '商业类', 'option_d': '历史类'},
        {'content': '你对未来职业的期望是？', 'category': '商业管理',
         'option_a': '技术专家', 'option_b': '企业管理者',
         'option_c': '自由职业者', 'option_d': '公务员'},
    ]
    for i, q in enumerate(questions):
        if not AssessmentQuestion.objects.filter(content=q['content']).exists():
            AssessmentQuestion.objects.create(order=i + 1, **q)
    print(f"  已创建 {len(questions)} 道测评题目")


def create_recommend_records():
    """创建推荐记录"""
    print("创建推荐记录...")
    students = User.objects.filter(role='student')
    universities = list(University.objects.all())
    count = 0
    for student in students:
        if not student.score:
            continue
        selected = random.sample(universities, min(9, len(universities)))
        for i, uni in enumerate(selected):
            if i < 3:
                level = 'rush'
                prob = round(random.uniform(20, 44), 1)
            elif i < 6:
                level = 'stable'
                prob = round(random.uniform(45, 74), 1)
            else:
                level = 'safe'
                prob = round(random.uniform(75, 95), 1)
            RecommendRecord.objects.create(
                user=student, university=uni, level=level,
                score=student.score, probability=prob,
                reason=f"基于历年录取数据智能推荐，录取概率{prob}%"
            )
            count += 1
    print(f"  已创建 {count} 条推荐记录")


def create_volunteer_forms():
    """创建志愿表"""
    print("创建志愿表...")
    students = User.objects.filter(role='student')
    universities = list(University.objects.all())
    count = 0
    for student in students:
        if not student.score:
            continue
        form = VolunteerForm.objects.create(
            user=student, name=f"{student.username}的志愿表",
            score=student.score, province=student.province,
            subject_type=student.subject_type or '物理类',
            status='analyzed',
            analysis='{"suggestions":["志愿梯度合理，冲稳保搭配较好"]}'
        )
        selected = random.sample(universities, min(6, len(universities)))
        for i, uni in enumerate(selected):
            majors = list(uni.majors.all())
            major = random.choice(majors) if majors else None
            VolunteerItem.objects.create(
                form=form, order=i + 1, university=uni, major=major,
                level=['rush', 'rush', 'stable', 'stable', 'safe', 'safe'][i],
                probability=round(random.uniform(20, 95), 1)
            )
            count += 1
    print(f"  已创建志愿表和 {count} 个志愿项")


def create_crawler_tasks():
    """创建爬虫任务"""
    print("创建爬虫任务...")
    tasks = [
        {'name': '2024年院校基本信息采集', 'task_type': 'university',
         'status': 'success', 'total_count': 25, 'success_count': 25,
         'log': '采集完成，共获取25所院校信息'},
        {'name': '2024年录取分数线采集', 'task_type': 'score',
         'status': 'success', 'total_count': 500, 'success_count': 498, 'fail_count': 2,
         'log': '采集完成，成功498条，失败2条'},
        {'name': '2025年招生计划采集', 'task_type': 'plan',
         'status': 'success', 'total_count': 200, 'success_count': 200,
         'log': '采集完成，共获取200条招生计划'},
        {'name': '专业信息更新', 'task_type': 'major',
         'status': 'pending', 'total_count': 0, 'success_count': 0,
         'log': '等待执行'},
    ]
    for t in tasks:
        if not CrawlerTask.objects.filter(name=t['name']).exists():
            CrawlerTask.objects.create(**t)
    print(f"  已创建 {len(tasks)} 个爬虫任务")


def create_system_data():
    """创建系统管理数据"""
    print("创建系统管理数据...")

    permissions = [
        {'role': 'student', 'module': '院校查询', 'can_view': True, 'can_edit': False,
         'can_delete': False, 'can_export': True, 'data_scope': 'all'},
        {'role': 'student', 'module': '志愿填报', 'can_view': True, 'can_edit': True,
         'can_delete': True, 'can_export': True, 'data_scope': 'self'},
        {'role': 'student', 'module': '智能推荐', 'can_view': True, 'can_edit': False,
         'can_delete': False, 'can_export': True, 'data_scope': 'self'},
        {'role': 'teacher', 'module': '院校查询', 'can_view': True, 'can_edit': False,
         'can_delete': False, 'can_export': True, 'data_scope': 'all'},
        {'role': 'teacher', 'module': '数据对比', 'can_view': True, 'can_edit': False,
         'can_delete': False, 'can_export': True, 'data_scope': 'all'},
        {'role': 'parent', 'module': '院校查询', 'can_view': True, 'can_edit': False,
         'can_delete': False, 'can_export': True, 'data_scope': 'all'},
        {'role': 'data_admin', 'module': '数据管理', 'can_view': True, 'can_edit': True,
         'can_delete': True, 'can_export': True, 'data_scope': 'all'},
        {'role': 'data_admin', 'module': '爬虫管理', 'can_view': True, 'can_edit': True,
         'can_delete': False, 'can_export': True, 'data_scope': 'all'},
        {'role': 'data_admin', 'module': '模型训练', 'can_view': True, 'can_edit': True,
         'can_delete': False, 'can_export': True, 'data_scope': 'all'},
        {'role': 'sys_admin', 'module': '全部模块', 'can_view': True, 'can_edit': True,
         'can_delete': True, 'can_export': True, 'data_scope': 'all'},
    ]
    for p in permissions:
        if not DataPermission.objects.filter(role=p['role'], module=p['module']).exists():
            DataPermission.objects.create(**p)

    configs = [
        {'key': 'site_name', 'value': '高考志愿智能推荐平台', 'description': '站点名称'},
        {'key': 'max_volunteer_count', 'value': '96', 'description': '最大志愿数'},
        {'key': 'current_year', 'value': '2025', 'description': '当前高考年份'},
        {'key': 'recommend_count', 'value': '10', 'description': '每级推荐数量'},
    ]
    for c in configs:
        SystemConfig.objects.update_or_create(key=c['key'], defaults=c)

    train_logs = [
        {'name': '录取概率预测模型v1', 'status': 'success', 'data_count': 5000,
         'accuracy': 87.5, 'log': '训练完成，准确率87.5%'},
        {'name': '录取概率预测模型v2', 'status': 'success', 'data_count': 8000,
         'accuracy': 91.2, 'log': '训练完成，准确率91.2%'},
        {'name': '专业推荐模型v1', 'status': 'pending', 'data_count': 0,
         'log': '等待训练'},
    ]
    for t in train_logs:
        if not ModelTrainLog.objects.filter(name=t['name']).exists():
            ModelTrainLog.objects.create(**t)


    logs = [
        {'username': 'student1', 'action': '登录', 'module': '用户认证', 'detail': '用户student1登录系统'},
        {'username': 'student1', 'action': '智能推荐', 'module': '推荐系统', 'detail': '执行智能匹配推荐，分数620'},
        {'username': 'student1', 'action': '志愿填报', 'module': '志愿管理', 'detail': '创建志愿表并提交'},
        {'username': 'teacher1', 'action': '登录', 'module': '用户认证', 'detail': '用户teacher1登录系统'},
        {'username': 'teacher1', 'action': '数据查询', 'module': '院校数据', 'detail': '查询北京大学录取分数线'},
        {'username': 'teacher1', 'action': '对比分析', 'module': '院校数据', 'detail': '对比北京大学和清华大学'},
        {'username': 'dataadmin', 'action': '登录', 'module': '用户认证', 'detail': '用户dataadmin登录系统'},
        {'username': 'dataadmin', 'action': '数据更新', 'module': '数据管理', 'detail': '更新2024年录取分数线'},
        {'username': 'dataadmin', 'action': '启动爬虫', 'module': '爬虫管理', 'detail': '启动院校信息采集任务'},
        {'username': 'dataadmin', 'action': '模型训练', 'module': '模型管理', 'detail': '启动录取概率预测模型训练'},
        {'username': 'sysadmin', 'action': '登录', 'module': '用户认证', 'detail': '用户sysadmin登录系统'},
        {'username': 'sysadmin', 'action': '权限配置', 'module': '系统管理', 'detail': '更新数据管理员权限配置'},
        {'username': 'sysadmin', 'action': '用户管理', 'module': '系统管理', 'detail': '重置用户密码'},
    ]
    for log in logs:
        user = User.objects.filter(username=log['username']).first()
        OperationLog.objects.create(
            user=user, username=log['username'],
            action=log['action'], module=log['module'],
            detail=log['detail'], ip_address='127.0.0.1'
        )
    print("  系统管理数据创建完成")


if __name__ == '__main__':
    print("=" * 50)
    print("开始初始化演示数据...")
    print("=" * 50)
    create_users()
    create_universities()
    create_majors()
    create_admission_scores()
    create_enrollment_plans()
    create_assessment_questions()
    create_recommend_records()
    create_volunteer_forms()
    create_crawler_tasks()
    create_system_data()
    print("=" * 50)
    print("演示数据初始化完成!")
    print("=" * 50)
    print("\n账号信息：")
    print("高考生: student1/123456, student2/123456, student3/123456")
    print("教师: teacher1/123456")
    print("家长: parent1/123456")
    print("数据管理员: dataadmin/123456")
    print("系统管理员: sysadmin/123456")
