from django.urls import path
from django.views.generic import TemplateView

from .views import contratos_view


app_name = 'contratos'

urlpatterns = [
    path('', TemplateView.as_view(template_name='contratos/base_contratos.html'), name='inicio_contratos'),
    path('registrar_contrato/', contratos_view.contratoView, name='novo_contrato'),  
]