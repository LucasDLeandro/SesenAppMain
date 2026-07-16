from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SystemLogViewSet

app_name = 'logs'

router = DefaultRouter()
router.register(r'system-logs', SystemLogViewSet, basename='systemlog')

urlpatterns = [
    path('api/', include(router.urls)),
]
