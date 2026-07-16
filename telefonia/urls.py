from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'telefonia'

router = DefaultRouter()
router.register(r'solicitacoes', views.TelefoneSolicitacaoViewSet, basename='solicitacao-telefone')
router.register(r'remessas', views.RemessaManutencaoViewSet, basename='remessa-manutencao')
router.register(r'senhas', views.CriarSenhaViewSet, basename='criar-senha')
router.register(r'contratos', views.ContratoColaboradorViewSet, basename='contrato-colaborador')

urlpatterns = [
    path('', views.main_telefonia, name='inicio_telefonia'),
    path('api/', include(router.urls)),
    path('api/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('remessa/<int:pk>/pdf/', views.gerar_pdf_remessa, name='gerar_pdf_remessa'),
    path('senha/<int:pk>/pdf/', views.gerar_pdf_senha, name='gerar_pdf_senha'),
    path('senha/<int:pk>/email/', views.enviar_email_senha_manual, name='enviar_email_senha_manual'),
    path('tutorial/pdf/', views.gerar_pdf_tutorial, name='gerar_pdf_tutorial'),
    path('preview/senha/<int:template_id>/pdf/', views.preview_pdf_senha_template, name='preview_pdf_senha_template'),
    path('preview/tutorial/<int:template_id>/pdf/', views.preview_pdf_tutorial_template, name='preview_pdf_tutorial_template'),
]
