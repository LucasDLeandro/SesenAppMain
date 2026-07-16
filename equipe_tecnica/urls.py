from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'equipe_tecnica'

router = DefaultRouter()
router.register(r'tecnicos', views.TecnicoViewSet, basename='tecnico')
router.register(r'solicitacoes', views.SolicitacaoAcessoViewSet, basename='solicitacao')
router.register(r'liberacoes', views.LiberacaoAcessoDiariaViewSet, basename='liberacao')

urlpatterns = [
    path('', views.dashboard_acessos, name='dashboard_acessos'),
    path('api/', include(router.urls)),
]
