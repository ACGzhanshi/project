"""系统管理序列化器"""
from rest_framework import serializers
from .models import OperationLog, DataPermission, SystemConfig, ModelTrainLog


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    class Meta:
        model = OperationLog
        fields = '__all__'


class DataPermissionSerializer(serializers.ModelSerializer):
    """数据权限序列化器"""
    class Meta:
        model = DataPermission
        fields = '__all__'


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    class Meta:
        model = SystemConfig
        fields = '__all__'


class ModelTrainLogSerializer(serializers.ModelSerializer):
    """模型训练日志序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ModelTrainLog
        fields = '__all__'
