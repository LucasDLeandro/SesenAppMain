"""
URL configuration for sesen_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from os import name
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from usuarios.views import login_view, logout_view, trocar_senha_view
from .views import hub_servicos_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path('', TemplateView.as_view(template_name='inicio.html'), name='inicio'),
    path('elevadores/', include('elevadores.urls', namespace='elevadores')),
    path('telefonia/', include('telefonia.urls', namespace='telefonia')),
    path('reembolsos/', include('reembolsos.urls', namespace='reembolsos')),
    path('audiovideo/', include('audiovideo.urls', namespace='audiovideo')),
    path('logs/', include('logs.urls')),
    path('contratos/', include('contratos.urls', namespace='contratos')),
    path('notificacoes/', include('notificacoes.urls', namespace='notificacoes')),
    path('adm_setup/', include('adm_setup.urls', namespace='sys_config')),
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('gestao_patrimonio/', include('gestao_patrimonio.urls', namespace='gestao_patrimonio')),
    path('empresas/', include('empresas.urls', namespace='empresas')),
    path('equipe_tecnica/', include('equipe_tecnica.urls', namespace='equipe_tecnica')),
    path('monitoramento-sei/', include('monitoramento_sei.urls', namespace='monitoramento_sei')),

    path('hub_servicos/', hub_servicos_view, name='hub_servicos'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('trocar-senha/', trocar_senha_view, name='trocar_senha'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Essa é a rota de Login!
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh') # Rota para renovar o token
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
