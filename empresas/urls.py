from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'empresas'

router = DefaultRouter()
router.register(r'empresas', views.EmpresaViewSet, basename='empresa')
router.register(r'contatos', views.ContatoEmpresaViewSet, basename='contato')

urlpatterns = [
    path('', views.dashboard_empresas, name='dashboard_empresas'),
    path('api/', include(router.urls)),
    path('api/contatos_por_app/', views.get_contatos_por_app, name='contatos_por_app'),
]
