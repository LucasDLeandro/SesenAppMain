from django.urls import path
from django.views.generic import TemplateView
from .views import conf_whats_notif_view, configuracao_geral_view, logs_view, configuracao_telefonia_view, configuracao_tutorial_view, configuracao_acessos_view, bulk_contatos_view

app_name = 'adm_setup'

urlpatterns = [
    path('', TemplateView.as_view(template_name='setups/sys_config_home.html'), name='sys_config'),
    path('configuracao-geral/', configuracao_geral_view.configuracao_geral_view, name='configuracao_geral'),
    path('configuracao-telefonia/', configuracao_telefonia_view.configuracao_telefonia_view, name='configuracao_telefonia'),
    path('configuracao-tutorial-telefonia/', configuracao_tutorial_view.configuracao_tutorial_telefonia_view, name='configuracao_tutorial'),
    path('configuracao-acessos/', configuracao_acessos_view.configuracao_acessos, name='configuracao_acessos'),
    path('notificacao_elev/', conf_whats_notif_view.gerenciar_notificacao, name='config_notificacao_whats'),
    path('bulk-contatos/', bulk_contatos_view.bulk_contatos_view, name='bulk_contatos'),
    path('logs/', logs_view.logs_list_view, name='logs_list'),
]