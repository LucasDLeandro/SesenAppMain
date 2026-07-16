from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import dashboard_audiovideo, EventoAVViewSet, OrdemServicoAVViewSet

app_name = 'audiovideo'

router = DefaultRouter()
router.register(r'eventos', EventoAVViewSet)
router.register(r'os', OrdemServicoAVViewSet)

urlpatterns = [
    path('dashboard/', dashboard_audiovideo, name='dashboard'),
    path('api/', include(router.urls)),
]
