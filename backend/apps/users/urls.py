"""用户路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserManageViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('manage', UserManageViewSet, basename='user-manage')

urlpatterns = [
    path('', include(router.urls)),
]
