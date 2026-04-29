""" service_orders URL Configuration """

from django.urls import path

from .views import elev_list_os_view, elev_so_view, ordens_view, cat_serv_view

from . import views

app_name = 'service_orders'

urlpatterns = [
    #path('', views.index, name='index'),
    path('categorias_e_servicos/', cat_serv_view.cat_serv_view, name='cat_serv_list'),
    path('', ordens_view.main_ordens, name='main_ordens'),
    path('elevadores/', elev_list_os_view.elev_list_os, name='elev_list_os'),
    path('api/oss/criarElevOs/', elev_so_view.api_elev_criar_os, name='api_criar_elev_os'),
    path('api/elev/dadosDashboard/', elev_so_view.api_elev_dashboard, name='api_elev_dados_dashboard'),
    path('api/oss/concluirElevOs/<int:id_elev_os>/', elev_so_view.api_elev_concluir_os, name='api_concluir_elev_os'),
    path('api/os/listaOs/api_elev_concluidas', elev_so_view.api_elev_concluidas, name='api_elev_concluidas'),
    #path('api/os/listaOs/api_indicador_um', elev_so_view.api_dados_indicador_um, name='api_dados_indicador_um'),
    #path('api/os/listaOs/api_indicador_tres', elev_so_view.api_dados_indicador_tres, name='api_dados_indicador_tres'),
    path('api/os/graficoMensal/', elev_so_view.api_grafico_qnt, name='api_grafico_qnt'),
    #path('api/oss/editarElevOs/<int:id_elev_os>/', elev_so_view.editarElevOs, name='api_editar_elev_os'),
    
]