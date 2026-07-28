from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet
from . import views

app_name = 'usuarios'

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuario')

from .api_views import global_contacts_search_api, buscar_dados_pessoa_api

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/global-contacts/search/', global_contacts_search_api, name='global_contacts_search'),
    path('api/pessoas/buscar-dados/', buscar_dados_pessoa_api, name='buscar_dados_pessoa'),
    path('gestao/', views.gestao_usuarios, name='gestao_usuarios'),
    path('meu-perfil/', views.meu_perfil_view, name='meu_perfil'),
]
