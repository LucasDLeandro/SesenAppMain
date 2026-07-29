from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardSEIView, ProcessoSEIViewSet

app_name = 'monitoramento_sei'

router = DefaultRouter()
router.register(r'processos', ProcessoSEIViewSet, basename='processos')

urlpatterns = [
    path('dashboard/', DashboardSEIView.as_view(), name='dashboard'),
    path('api/', include(router.urls)),
]
