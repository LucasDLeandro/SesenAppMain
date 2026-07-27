from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.contratos_view import (
    dashboard_contratos, 
    home_contratos,
    dashboard_metrics,
    dashboard_contratacoes,
    dashboard_contratacoes_metrics,
    ContratoViewSet, 
    ProcessoLicitatorioViewSet,
    MedicaoMensalViewSet,
    PagamentoViewSet,
    TramitacaoSEIViewSet,
    CronogramaContratacaoViewSet,
    buscar_contratos_comprasnet
)

app_name = 'contratos'

router = DefaultRouter()
router.register(r'processos', ProcessoLicitatorioViewSet, basename='processo')
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'medicoes', MedicaoMensalViewSet, basename='medicao')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')
router.register(r'tramitacoes', TramitacaoSEIViewSet, basename='tramitacao')
router.register(r'cronogramas', CronogramaContratacaoViewSet, basename='cronograma')

urlpatterns = [
    path('', home_contratos, name='home'),
    path('lista/', dashboard_contratos, name='dashboard_contratos'),
    path('contratacoes/', dashboard_contratacoes, name='dashboard_contratacoes'),
    path('api/dashboard-metrics/', dashboard_metrics, name='dashboard_metrics'),
    path('api/dashboard-contratacoes-metrics/', dashboard_contratacoes_metrics, name='dashboard_contratacoes_metrics'),
    path('api/comprasnet/contratos/', buscar_contratos_comprasnet, name='buscar_contratos_comprasnet'),
    path('api/', include(router.urls)),
]