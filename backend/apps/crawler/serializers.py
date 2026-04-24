"""爬虫模块序列化器"""
from rest_framework import serializers
from .models import CrawlerTask, CrawlerData


class CrawlerTaskSerializer(serializers.ModelSerializer):
    """爬虫任务序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_task_type_display', read_only=True)

    class Meta:
        model = CrawlerTask
        fields = '__all__'


class CrawlerDataSerializer(serializers.ModelSerializer):
    """爬取数据序列化器"""
    class Meta:
        model = CrawlerData
        fields = '__all__'
