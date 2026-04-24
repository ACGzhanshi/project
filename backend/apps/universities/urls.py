"""院校路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UniversityViewSet, MajorViewSet,
    AdmissionScoreViewSet, EnrollmentPlanViewSet
)

router = DefaultRouter()
router.register('list', UniversityViewSet, basename='university')
router.register('majors', MajorViewSet, basename='major')
router.register('scores', AdmissionScoreViewSet, basename='score')
router.register('plans', EnrollmentPlanViewSet, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
]
