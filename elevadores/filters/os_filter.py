import django_filters
from django import forms

from ..models.elev_so_model import ElevOrderReg

class OsFilter(django_filters.FilterSet):
    data_inicio = django_filters.DateTimeFilter(
        field_name='data_hora',
        lookup_expr='gte',
        label="Data Início",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )

    data_fim = django_filters.DateTimeFilter(
        field_name='data_hora',
        lookup_expr='lte',
        label="Data Fim",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )

    

        

        