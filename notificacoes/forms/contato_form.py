from django import forms

from ..models.contato_notificacao import Contato

class CriarContatoForm(forms.ModelForm):
    nome = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}), label='Nome')
    telefone = forms.CharField(max_length=13, widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '13'}), label='Telefone - nº WhatsApp', required=False)
    email = forms.EmailField(max_length=150, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: email@dominio.com'}), label='E-mail', required=False)

    class Meta:
        model = Contato
        fields = [
            'id',
            'role',
            'notifica_elevadores',
            'notifica_telefonia',
            'receber_whatsapp',
            'receber_email',
            'is_ativo'
            ]
        
        widgets = {
            'id': forms.HiddenInput(),
            'role': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}),
            'notifica_elevadores': forms.CheckboxInput(attrs={'type': 'checkbox'}),
            'notifica_telefonia': forms.CheckboxInput(attrs={'type': 'checkbox'}),
            'receber_whatsapp': forms.CheckboxInput(attrs={'type': 'checkbox'}),
            'receber_email': forms.CheckboxInput(attrs={'type': 'checkbox'}),
            'is_ativo': forms.CheckboxInput(attrs={'type': 'checkbox', 'id': 'id_contato_is_ativo'}),
        }

        labels = {
            'id': 'ID - Contato',
            'role': 'Tipo de Contato',
            'notifica_elevadores': 'Recebe Notificações de Elevadores',
            'notifica_telefonia': 'Recebe Notificações de Telefonia',
            'receber_whatsapp': 'Receber por WhatsApp',
            'receber_email': 'Receber por E-mail',
            'is_ativo': 'Ativo?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.pessoa:
            self.fields['nome'].initial = self.instance.pessoa.nome
            self.fields['telefone'].initial = self.instance.pessoa.telefone
            self.fields['email'].initial = self.instance.pessoa.email

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
        email = self.cleaned_data.get('email')
        
        if contato.pessoa:
            contato.pessoa.nome = nome
            contato.pessoa.telefone = telefone
            contato.pessoa.email = email
            contato.pessoa.save()
        else:
            pessoa, _ = Pessoa.objects.get_or_create(
                nome=nome,
                defaults={'telefone': telefone, 'email': email}
            )
            # Caso a pessoa já existisse mas os dados não estivessem atualizados (ex: sem email)
            if not _ :
                pessoa.telefone = telefone
                pessoa.email = email
                pessoa.save()
                
            contato.pessoa = pessoa
            
        if commit:
            contato.save()
        return contato