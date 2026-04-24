"""爬虫模块路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrawlerTaskViewSet

router = DefaultRouter()
router.register('tasks', CrawlerTaskViewSet, basename='crawler-task')

urlpatterns = [
    path('', include(router.urls)),
]
