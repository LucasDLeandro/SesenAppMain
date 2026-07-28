from django import forms

from ..models.contato_notificacao import Contato

class CriarContatoForm(forms.ModelForm):
    nome = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}), label='Nome')
    telefone = forms.CharField(max_length=13, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '13'}), label='Telefone - nº WhatsApp', required=False)

    class Meta:
        model = Contato
        fields = [
            'id',
            'role',
            'is_ativo'
            ]
        
        widgets = {
            'id': forms.HiddenInput(),
            'role': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}),
            'is_ativo': forms.CheckboxInput(attrs={'type': 'checkbox', 'id': 'id_contato_is_ativo'}),
        }

        labels = {
            'id': 'ID - Contato',
            'role': 'Tipo de Contato',
            'is_ativo': 'Ativo?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.pessoa:
            self.fields['nome'].initial = self.instance.pessoa.nome
            self.fields['telefone'].initial = self.instance.pessoa.telefone

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            import re
            telefone = re.sub(r'\D', '', telefone)
            if len(telefone) in (10, 11) and not telefone.startswith('55'):
                telefone = f"55{telefone}"
        return telefone

    def save(self, commit=True):
        contato = super().save(commit=False)
        from usuarios.models import Pessoa
        
        nome = self.cleaned_data.get('nome')
        telefone = self.cleaned_data.get('telefone')
        
        if contato.pessoa:
            contato.pessoa.nome = nome
            contato.pessoa.telefone = telefone
            contato.pessoa.save()
        else:
            pessoa, _ = Pessoa.objects.get_or_create(
                nome=nome,
                defaults={'telefone': telefone}
            )
            contato.pessoa = pessoa
            
        if commit:
            contato.save()
        return contato