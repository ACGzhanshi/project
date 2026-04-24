"""志愿填报路由"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VolunteerFormViewSet

router = DefaultRouter()
router.register('forms', VolunteerFormViewSet, basename='volunteer-form')

urlpatterns = [
    path('', include(router.urls)),
]
