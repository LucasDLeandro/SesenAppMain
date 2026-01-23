""" service_orders URL Configuration """

from django.urls import path

from .views import create_os_view, list_os_view, ordens_view, cat_serv_view

from . import views

app_name = 'service_orders'

urlpatterns = [
    #path('', views.index, name='index'),
    path('categorias_e_servicos/', cat_serv_view.cat_serv_view, name='cat_serv_list'),
    path('registrar_os', create_os_view.create_os, name='create_os'),
    path('', ordens_view.main_ordens, name='main_ordens'),
    path('list/', list_os_view.list_os, name='list_os'),

]