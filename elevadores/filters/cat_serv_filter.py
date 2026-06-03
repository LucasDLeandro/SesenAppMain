import django_filters
from django import forms

from ..models.mapa_servicos import Categoria, Servico

class CatServFilter(django_filters.FilterSet):
    nome_categoria = django_filters.CharFilter(
        field_name = 'nome_categoria',
        lookup_expr = 'icontains',
        label = 'Categoria',
        widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
    )

    descricao_categoria = django_filters.CharFilter(
        field_name = 'descricao_categoria',
        lookup_expr = 'icontains',
        label = 'Descrição - Categoria',
        widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
    )

    nome_servico = django_filters.CharFilter(
        field_name = 'nome_servico',
        lookup_expr = 'icontains',
        label = 'Categoria',
        widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
    )

    descricao_servico = django_filters.CharFilter(
        field_name = 'descricao_servico',
        lookup_expr = 'icontains',
        label = 'Descrição - Categoria',
        widget = forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
    )
    