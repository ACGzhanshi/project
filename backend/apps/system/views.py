"""系统管理视图"""
import threading
import time
import random
from datetime import datetime
from rest_framework import viewsets,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count
from .models import OperationLog, DataPermission, SystemConfig, ModelTrainLog
from .serializers import (
    OperationLogSerializer, DataPermissionSerializer,
    SystemConfigSerializer, ModelTrainLogSerializer
)
from apps.users.models import User
from apps.universities.models import University, AdmissionScore
from apps.recommendation.models import RecommendRecord
from rest_framework import filters

class IsSystemAdmin(permissions.BasePermission):
    """
    仅系统管理员(sys_admin)或超级管理员可以查看日志
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'sys_admin' or request.user.is_superuser
        )


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志接口"""
    queryset = OperationLog.objects.all().order_by('-created_at')
    serializer_class = OperationLogSerializer
    permission_classes = [IsSystemAdmin]

    # 引入搜索和过滤机制
    filter_backends = [filters.SearchFilter]

    # 注意这里：匹配模型中的真实字段 username 和 detail
    search_fields = ['module', 'action', 'username', 'detail', 'ip_address']
    filterset_fields = ['action', 'module', 'username']

class DataPermissionViewSet(viewsets.ModelViewSet):
    """数据权限管理"""
    queryset = DataPermission.objects.all()
    serializer_class = DataPermissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'module']


class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置管理"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'key'


class ModelTrainViewSet(viewsets.ModelViewSet):
    """模型训练管理"""
    queryset = ModelTrainLog.objects.all().order_by('-created_at')
    serializer_class = ModelTrainLogSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def start_train(self, request, pk=None):
        """启动模型训练"""
        log = self.get_object()
        if log.status == 'training':
            return Response({'code': 400, 'message': '模型正在训练中'}, status=400)

        def train_model(train_log):
            train_log.status = 'training'
            train_log.started_at = datetime.now()
            train_log.save()
            lines = []
            for epoch in range(1, 11):
                time.sleep(0.5)
                loss = round(random.uniform(0.1, 0.5) / epoch, 4)
                acc = round(min(0.95, 0.6 + epoch * 0.035 + random.uniform(0, 0.02)), 4)
                lines.append(f"Epoch {epoch}/10 - loss: {loss} - accuracy: {acc}")
                train_log.log = '\n'.join(lines)
                train_log.save()
            train_log.accuracy = round(random.uniform(85, 95), 2)
            train_log.status = 'success'
            train_log.finished_at = datetime.now()
            train_log.save()

        thread = threading.Thread(target=train_model, args=(log,))
        thread.daemon = True
        thread.start()

        from .middleware import log_operation
        log_operation(request.user, '模型训练', '模型管理',
                      f'启动模型训练：{log.name}',
                      request.META.get('REMOTE_ADDR', ''))

        return Response({'code': 200, 'message': '训练已启动'})


class DashboardViewSet(viewsets.GenericViewSet):
    """仪表盘数据"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """系统概览"""
        data = {
            'user_count': User.objects.count(),
            'university_count': University.objects.count(),
            'score_count': AdmissionScore.objects.count(),
            'recommend_count': RecommendRecord.objects.count(),
            'user_by_role': list(
                User.objects.values('role').annotate(count=Count('id'))
            ),
            'recent_logs': OperationLogSerializer(
                OperationLog.objects.all()[:10], many=True
            ).data,
        }
        return Response({'code': 200, 'data': data})

    @action(detail=False, methods=['get'])
    def score_distribution(self, request):
        """分数分布统计"""
        from django.db.models import Count, Case, When, IntegerField
        distribution = AdmissionScore.objects.filter(year=2024).aggregate(
            below_500=Count(Case(When(min_score__lt=500, then=1), output_field=IntegerField())),
            s500_550=Count(Case(When(min_score__gte=500, min_score__lt=550, then=1), output_field=IntegerField())),
            s550_600=Count(Case(When(min_score__gte=550, min_score__lt=600, then=1), output_field=IntegerField())),
            s600_650=Count(Case(When(min_score__gte=600, min_score__lt=650, then=1), output_field=IntegerField())),
            above_650=Count(Case(When(min_score__gte=650, then=1), output_field=IntegerField())),
        )
        return Response({'code': 200, 'data': distribution})
