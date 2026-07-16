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
            'is_ativo': forms.CheckboxInput(attrs={'type': 'checkbox', 'id': 'id_contato_is_ativo'}),
        }

        labels = {
            'id': 'ID - Contato',
            'nome': 'Nome',
            'telefone': 'Telefone - nº WhatsApp',
            'role': 'Tipo de Contato',
            'is_ativo': 'Ativo?'
        }

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            import re
            telefone = re.sub(r'\D', '', telefone)
            if len(telefone) in (10, 11) and not telefone.startswith('55'):
                telefone = f"55{telefone}"
        return telefone