from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'clientes'

# Rotas da API
router = DefaultRouter()
router.register(r'api/clientes', views.ClienteViewSet, basename='api-clientes')
router.register(r'api/pedidos', views.PedidoViewSet, basename='api-pedidos')

urlpatterns = [
    # Rotas HTML
    path('', views.clientes_view, name='list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Inclusão das rotas da API
    path('', include(router.urls)),
]
