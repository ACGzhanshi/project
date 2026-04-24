"""主路由配置"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/universities/', include('apps.universities.urls')),
    path('api/recommendation/', include('apps.recommendation.urls')),
    path('api/volunteer/', include('apps.volunteer.urls')),
    path('api/crawler/', include('apps.crawler.urls')),
    path('api/system/', include('apps.system.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
