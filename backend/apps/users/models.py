"""用户模型定义"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型，支持多角色"""

    ROLE_CHOICES = (
        ('student', '高考生'),
        ('teacher', '教师'),
        ('parent', '家长'),
        ('data_admin', '数据管理员'),
        ('sys_admin', '系统管理员'),
    )

    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField('手机号', max_length=11, blank=True, default='')
    province = models.CharField('省份', max_length=20, blank=True, default='')
    score = models.IntegerField('高考分数', null=True, blank=True)
    subject_type = models.CharField('科目类型', max_length=10, blank=True, default='')
    subjects = models.CharField('选考科目', max_length=100, blank=True, default='')
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.username}({self.get_role_display()})"
