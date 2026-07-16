from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'gestao_patrimonio'

router = DefaultRouter()
router.register(r'tvs', views.TVViewSet, basename='tv')
router.register(r'aparelhos-telefonicos', views.AparelhoTelefonicoViewSet, basename='telefone')
router.register(r'equipamentos-av', views.EquipamentoAVViewSet, basename='equipamento-av')
router.register(r'transferencias', views.TransferenciaPatrimonioViewSet, basename='transferencia')

urlpatterns = [
    path('transferencias/', views.dashboard_transferencias, name='dashboard_transferencias'),
    path('api/equipamentos-base/', views.EquipamentoBaseView.as_view(), name='equipamento-base'),
    path('api/', include(router.urls)),
]
