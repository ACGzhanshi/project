"""系统管理模型"""
from django.db import models
from apps.users.models import User


class OperationLog(models.Model):
    """操作日志"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作用户')
    username = models.CharField('用户名', max_length=50)
    action = models.CharField('操作类型', max_length=50)
    module = models.CharField('操作模块', max_length=50)
    detail = models.TextField('操作详情', blank=True, default='')
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class DataPermission(models.Model):
    """数据权限配置"""
    role = models.CharField('角色', max_length=20)
    module = models.CharField('模块', max_length=50)
    can_view = models.BooleanField('可查看', default=True)
    can_edit = models.BooleanField('可编辑', default=False)
    can_delete = models.BooleanField('可删除', default=False)
    can_export = models.BooleanField('可导出', default=False)
    data_scope = models.CharField('数据范围', max_length=50, default='all')
    remark = models.TextField('备注', blank=True, default='')

    class Meta:
        db_table = 'data_permissions'
        verbose_name = '数据权限'
        verbose_name_plural = verbose_name


class SystemConfig(models.Model):
    """系统配置"""
    key = models.CharField('配置键', max_length=50, unique=True)
    value = models.TextField('配置值')
    description = models.CharField('说明', max_length=200, blank=True, default='')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name


class ModelTrainLog(models.Model):
    """模型训练日志"""
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('training', '训练中'),
        ('success', '训练完成'),
        ('failed', '训练失败'),
    )

    name = models.CharField('模型名称', max_length=100)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    data_count = models.IntegerField('训练数据量', default=0)
    accuracy = models.DecimalField('准确率', max_digits=5, decimal_places=2, null=True)
    params = models.JSONField('训练参数', null=True, blank=True)
    log = models.TextField('训练日志', blank=True, default='')
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'model_train_logs'
        verbose_name = '模型训练日志'
        verbose_name_plural = verbose_name
