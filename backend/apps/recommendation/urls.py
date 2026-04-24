"""推荐模块路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecommendViewSet, AssessmentViewSet
from .views import AssessmentQuestionViewSet
from . import views

router = DefaultRouter()
router.register('recommend', RecommendViewSet, basename='recommend')
router.register('assessment', AssessmentViewSet, basename='assessment')
router.register(r'questions', AssessmentQuestionViewSet)
urlpatterns = [
    path('ai_chat/', views.ai_chat, name='ai_chat'),
    path('', include(router.urls)),
]
