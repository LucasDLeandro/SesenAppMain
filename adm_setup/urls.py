from django.urls import path
from django.views.generic import TemplateView
from .views import conf_whats_notif_view

app_name = 'adm_setup'

urlpatterns = [
    path('', TemplateView.as_view(template_name='setups/base_setup.html'), name='sys_config'),
    path('notificacao_elev/', conf_whats_notif_view.gerenciar_notificacao, name='config_notificacao_whats')
]