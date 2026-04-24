"""志愿填报模型"""
from django.db import models
from apps.users.models import User
from apps.universities.models import University, Major


class VolunteerForm(models.Model):
    """志愿表"""
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('analyzed', '已分析'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='volunteer_forms', verbose_name='用户')
    name = models.CharField('志愿表名称', max_length=50)
    score = models.IntegerField('高考分数')
    province = models.CharField('省份', max_length=20)
    subject_type = models.CharField('科类', max_length=10)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    analysis = models.TextField('分析结果', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'volunteer_forms'
        verbose_name = '志愿表'
        verbose_name_plural = verbose_name


class VolunteerItem(models.Model):
    """志愿表项目"""
    form = models.ForeignKey(VolunteerForm, on_delete=models.CASCADE,
                             related_name='items', verbose_name='志愿表')
    order = models.IntegerField('志愿序号')
    university = models.ForeignKey(University, on_delete=models.CASCADE, verbose_name='院校')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True,
                              blank=True, verbose_name='专业')
    level = models.CharField('冲稳保', max_length=10, blank=True, default='')
    probability = models.DecimalField('录取概率', max_digits=5, decimal_places=2,
                                      null=True, blank=True)

    class Meta:
        db_table = 'volunteer_items'
        verbose_name = '志愿项'
        verbose_name_plural = verbose_name
        ordering = ['order']
