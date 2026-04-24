"""系统管理路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OperationLogViewSet, DataPermissionViewSet,
    SystemConfigViewSet, ModelTrainViewSet, DashboardViewSet
)

router = DefaultRouter()
router.register('logs', OperationLogViewSet, basename='operation-log')
router.register('permissions', DataPermissionViewSet, basename='data-permission')
router.register('configs', SystemConfigViewSet, basename='system-config')
router.register('model-train', ModelTrainViewSet, basename='model-train')
router.register('dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
