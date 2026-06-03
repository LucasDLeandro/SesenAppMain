from django import forms
from django.forms import inlineformset_factory

from ..models.mapa_servicos import Categoria, Servico

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Categoria
       
        fields = [
            'nome_categoria',
            'descricao_categoria'
        ]

        labels = {
            'nome_categoria': 'Categoria',
            'descricao_categoria': 'Descrição da Categoria'
        }

        widgets = {
            'nome_categoria': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control'
            }),
            'descricao_categoria': forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
                'rows': 1
            })
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = [
            'nome_servico',
            'descricao_servico'
        ]

        labels = {
            'nome_servico': 'Nome do Serviço',
            'descricao_servico': 'Descrição do Serviço'
        }

        widgets = {
            'nome_servico': forms.TextInput(attrs={
                'type': 'text',
                'class': 'form-control',
            }),
            'descricao_servico': forms.Textarea(attrs={
                'type': 'text',
                'class': 'form-control',
                'rows': 1,
            })
        }

ServiceFormSet = inlineformset_factory(
    Categoria,
    Servico,
    form = ServiceForm,
    extra = 3,
    can_delete = True,
)

