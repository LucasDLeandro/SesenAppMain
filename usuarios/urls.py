from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet
from . import views

app_name = 'usuarios'

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuario')

urlpatterns = [
    path('api/', include(router.urls)),
    path('gestao/', views.gestao_usuarios, name='gestao_usuarios'),
    path('meu-perfil/', views.meu_perfil_view, name='meu_perfil'),
]
