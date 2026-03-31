from django import forms

from ..models.contato_notificacao import Contato

class CriarContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = [
            'id',
            'nome',
            'telefone',
            'role',
            'is_ativo'
            ]
        
        widgets = {
            'id': forms.HiddenInput(),
            'nome': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}),
            'telefone': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '13'}),
            'role': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}),
            'is_ativo': forms.CheckboxInput(attrs={'type': 'checkbox'}),
        }

        labels = {
            'id': 'ID - Contato',
            'nome': 'Nome',
            'telefone': 'Telefone - nº WhatsApp',
            'role': 'Tipo de Contato',
            'is_ativo': 'Ativo?'
        }