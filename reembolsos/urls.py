from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'reembolsos'

router = DefaultRouter()
router.register(r'limites', views.LimiteReembolsoViewSet, basename='limites')
router.register(r'servidores', views.ServidorReembolsoViewSet, basename='servidor-reembolso')
router.register(r'solicitacoes', views.SolicitacaoReembolsoViewSet, basename='solicitacao-reembolso')

urlpatterns = [
    path('', views.dashboard_reembolsos, name='inicio_reembolsos'),
    path('api/', include(router.urls)),
    path('api/configuracao-pdf/', views.ConfiguracaoRelatorioAPIView.as_view(), name='configuracao-pdf'),
    path('relatorio/anual/<int:pk>/', views.gerar_pdf_controle_anual, name='pdf_controle_anual'),
    path('relatorio/solicitacao/<int:pk>/', views.gerar_pdf_solicitacao, name='pdf_solicitacao'),
]
