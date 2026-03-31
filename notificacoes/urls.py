from django.urls import path
from django.views.generic import TemplateView
from .views import adm_contato_view

app_name = 'notificacoes'

urlpatterns = [
    path('', TemplateView.as_view(template_name='messages/base_message.html'), name='notificacoes'),
    path('api/contatos/criarContato/', adm_contato_view.api_criar_contato, name='api_criar_contato'),
    path('api/contatos/editarContato/<int:id_contato>/', adm_contato_view.api_editar_contato, name='api_editar_contato')
    
]