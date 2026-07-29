from django.urls import path
from django.views.generic import TemplateView
from .views import adm_contato_view, adm_message_view

app_name = 'notificacoes'

urlpatterns = [
    path('', TemplateView.as_view(template_name='messages/base_message.html'), name='notificacoes'),
    path('api/contatos/criarContato/', adm_contato_view.api_criar_contato, name='api_criar_contato'),
    path('api/contatos/editarContato/<int:id_contato>/', adm_contato_view.api_editar_contato, name='api_editar_contato'),
    path('api/contatos/deletarContato/<int:id_contato>/', adm_contato_view.api_deletar_contato, name='api_deletar_contato'),
    path('api/pessoas/buscar/', adm_contato_view.api_buscar_pessoas, name='api_buscar_pessoas'),
    path('api/templates/criarTemplate/', adm_message_view.api_criar_template, name='api_criar_template'),
    path('api/templates/editarTemplate/<int:id_template>/', adm_message_view.api_editar_template, name='api_editar_template'),
    path('api/templates/deletarTemplate/<int:id_template>/', adm_message_view.api_deletar_template, name='api_deletar_template'),
]