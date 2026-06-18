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

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path('', TemplateView.as_view(template_name='index.html'), name='inicio'),
    path('elevadores/', include('elevadores.urls', namespace='elevadores')),
    path('contratos/', include('contratos.urls', namespace='contratos')),
    path('notificacoes/', include('notificacoes.urls', namespace='notificacoes')),
    path('adm_setup/', include('adm_setup.urls', namespace='sys_config')),

    path('hub_servicos/', TemplateView.as_view(template_name='base_hub_servicos.html'), name='hub_servicos'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Essa é a rota de Login!
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh') # Rota para renovar o token
]
