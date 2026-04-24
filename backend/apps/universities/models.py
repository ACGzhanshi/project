"""院校和专业数据模型"""
from django.db import models


class University(models.Model):
    """院校信息"""
    name = models.CharField('院校名称', max_length=100)
    code = models.CharField('院校代码', max_length=20, unique=True)
    province = models.CharField('所在省份', max_length=20)
    city = models.CharField('所在城市', max_length=30)
    level = models.CharField('办学层次', max_length=20)
    type = models.CharField('院校类型', max_length=20)
    is_985 = models.BooleanField('985院校', default=False)
    is_211 = models.BooleanField('211院校', default=False)
    is_double_first = models.BooleanField('双一流', default=False)
    website = models.URLField('官网', blank=True, default='')
    description = models.TextField('简介', blank=True, default='')
    ranking = models.IntegerField('排名', null=True, blank=True)
    employment_rate = models.DecimalField('就业率', max_digits=5, decimal_places=2, null=True)
    logo = models.ImageField('校徽', upload_to='university_logos/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'universities'
        verbose_name = '院校'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Major(models.Model):
    """专业信息"""
    university = models.ForeignKey(University, on_delete=models.CASCADE,
                                   related_name='majors', verbose_name='所属院校')
    name = models.CharField('专业名称', max_length=100)
    code = models.CharField('专业代码', max_length=20)
    category = models.CharField('学科门类', max_length=30)
    duration = models.IntegerField('学制', default=4)
    degree = models.CharField('授予学位', max_length=30, default='')
    description = models.TextField('专业简介', blank=True, default='')
    employment_rate = models.DecimalField('就业率', max_digits=5, decimal_places=2, null=True)
    avg_salary = models.IntegerField('平均薪资', null=True, blank=True)
    tuition = models.CharField('学费', max_length=50, null=True, blank=True)
    major_group = models.CharField('专业组/选科要求', max_length=100, null=True, blank=True)
    discipline_eval = models.CharField('学科评估结果', max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'majors'
        verbose_name = '专业'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.university.name}-{self.name}"


class StandardMajor(models.Model):
    """国家标准专业目录（大纲库）"""
    special_id = models.CharField('平台专业ID', max_length=20, unique=True)
    code = models.CharField('专业代码', max_length=20, null=True, blank=True)
    name = models.CharField('专业名称', max_length=100)

    level1_name = models.CharField('学历层次', max_length=50, null=True, blank=True)  # 如：本科(普通)
    level2_name = models.CharField('学科门类', max_length=50, null=True, blank=True)  # 如：工学
    level3_name = models.CharField('专业类', max_length=50, null=True, blank=True)  # 如：计算机类

    degree = models.CharField('授予学位', max_length=50, null=True, blank=True)
    years = models.CharField('修业年限', max_length=20, null=True, blank=True)

    # 核心统计数据
    salary_avg = models.IntegerField('全国平均起薪', null=True, blank=True)
    salary_5year = models.IntegerField('5年后平均薪资', null=True, blank=True)
    boy_rate = models.IntegerField('男生比例(%)', null=True, blank=True)
    girl_rate = models.IntegerField('女生比例(%)', null=True, blank=True)

    class Meta:
        verbose_name = '国家标准专业'
        verbose_name_plural = verbose_name

class AdmissionScore(models.Model):
    """录取分数线"""
    university = models.ForeignKey(University, on_delete=models.CASCADE,
                                   related_name='scores', verbose_name='院校')
    major = models.ForeignKey(Major, on_delete=models.CASCADE, null=True,
                              blank=True, related_name='scores', verbose_name='专业')
    year = models.IntegerField('年份')
    province = models.CharField('招生省份', max_length=20)
    subject_type = models.CharField('科类', max_length=10)
    batch = models.CharField('批次', max_length=20)
    min_score = models.IntegerField('最低分')
    max_score = models.IntegerField('最高分', null=True, blank=True)
    avg_score = models.IntegerField('平均分', null=True, blank=True)
    min_rank = models.IntegerField('最低位次', null=True, blank=True)
    plan_count = models.IntegerField('招生计划数', null=True, blank=True)
    actual_count = models.IntegerField('实际录取数', null=True, blank=True)

    class Meta:
        db_table = 'admission_scores'
        verbose_name = '录取分数线'
        verbose_name_plural = verbose_name
        # 防止重复插入同一条数据
        unique_together = ('university', 'major', 'year', 'province', 'batch', 'subject_type')

    def __str__(self):
        return f"{self.university.name} {self.year}年 {self.province}"


class EnrollmentPlan(models.Model):
    """招生计划"""
    university = models.ForeignKey(University, on_delete=models.CASCADE,
                                   related_name='plans', verbose_name='院校')
    major = models.ForeignKey(Major, on_delete=models.CASCADE, null=True,
                              blank=True, related_name='plans', verbose_name='专业')
    year = models.IntegerField('年份')
    province = models.CharField('招生省份', max_length=20)
    subject_type = models.CharField('科类', max_length=10)
    plan_count = models.IntegerField('计划人数')
    tuition = models.IntegerField('学费(元/年)', null=True, blank=True)
    remark = models.TextField('备注', blank=True, default='')

    class Meta:
        db_table = 'enrollment_plans'
        verbose_name = '招生计划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.university.name} {self.year}年招生计划"
