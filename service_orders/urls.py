""" service_orders URL Configuration """

from django.urls import path

from .views import create_os_view

from . import views

app_name = 'service_orders'

urlpatterns = [
    #path('', views.index, name='index'),
    path('', create_os_view.os_list),
]