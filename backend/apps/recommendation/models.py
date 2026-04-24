"""推荐模块模型"""
from django.db import models
from apps.users.models import User
from apps.universities.models import University, Major


class RecommendRecord(models.Model):
    """推荐记录"""
    LEVEL_CHOICES = (
        ('rush', '冲'),
        ('stable', '稳'),
        ('safe', '保'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='recommendations', verbose_name='用户')
    university = models.ForeignKey(University, on_delete=models.CASCADE, verbose_name='推荐院校')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True,
                              blank=True, verbose_name='推荐专业')
    level = models.CharField('推荐等级', max_length=10, choices=LEVEL_CHOICES)
    score = models.IntegerField('用户分数')
    probability = models.DecimalField('录取概率', max_digits=5, decimal_places=2)
    reason = models.TextField('推荐理由', blank=True, default='')
    created_at = models.DateTimeField('推荐时间', auto_now_add=True)

    class Meta:
        db_table = 'recommend_records'
        verbose_name = '推荐记录'
        verbose_name_plural = verbose_name


class AssessmentQuestion(models.Model):
    """专业测评题目"""
    content = models.TextField('题目内容')
    option_a = models.CharField('选项A', max_length=200)
    option_b = models.CharField('选项B', max_length=200)
    option_c = models.CharField('选项C', max_length=200)
    option_d = models.CharField('选项D', max_length=200)
    category = models.CharField('测评维度', max_length=30)
    order = models.IntegerField('排序', default=0)

    class Meta:
        db_table = 'assessment_questions'
        verbose_name = '测评题目'
        verbose_name_plural = verbose_name


class AssessmentResult(models.Model):
    """测评结果"""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='assessments', verbose_name='用户')
    answers = models.JSONField('答题记录')
    result = models.JSONField('测评结果')
    recommended_majors = models.TextField('推荐专业方向')
    created_at = models.DateTimeField('测评时间', auto_now_add=True)

    class Meta:
        db_table = 'assessment_results'
        verbose_name = '测评结果'
        verbose_name_plural = verbose_name
