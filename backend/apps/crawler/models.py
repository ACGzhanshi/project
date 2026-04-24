"""爬虫模块模型"""
from django.db import models


class CrawlerTask(models.Model):
    """爬虫任务"""
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failed', '失败'),
    )
    TYPE_CHOICES = (
        ('university', '院校信息'),
        ('score', '分数线'),
        ('plan', '招生计划'),
        ('major', '专业信息'),
    )

    name = models.CharField('任务名称', max_length=100)
    task_type = models.CharField('任务类型', max_length=20, choices=TYPE_CHOICES)
    target_url = models.URLField('目标地址', blank=True, default='')
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='pending')
    total_count = models.IntegerField('总数据量', default=0)
    success_count = models.IntegerField('成功数量', default=0)
    fail_count = models.IntegerField('失败数量', default=0)
    log = models.TextField('运行日志', blank=True, default='')
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'crawler_tasks'
        verbose_name = '爬虫任务'
        verbose_name_plural = verbose_name


class CrawlerData(models.Model):
    """爬取的原始数据"""
    task = models.ForeignKey(CrawlerTask, on_delete=models.CASCADE,
                             related_name='data_items', verbose_name='所属任务')
    data_type = models.CharField('数据类型', max_length=20)
    raw_data = models.JSONField('原始数据')
    is_cleaned = models.BooleanField('是否已清洗', default=False)
    cleaned_data = models.JSONField('清洗后数据', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'crawler_data'
        verbose_name = '爬取数据'
        verbose_name_plural = verbose_name
