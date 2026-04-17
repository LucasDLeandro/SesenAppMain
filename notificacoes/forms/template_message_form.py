from django import forms

from ..models.template_notificacao import TemplateMessage

class CriarTemplateForm(forms.ModelForm):
    class Meta:
        model = TemplateMessage
        fields = [
            "id",
            "tipo_evento",
            "id_template",
            "base_text", 
            "is_ativo"
        ]

        widgets = {
            'id': forms.HiddenInput(),
            'tipo_evento': forms.Select(attrs={'type': 'select', 'class': 'form-select'}),
            'id_template': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '100'}),
            'base_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 11}),
            'is_ativo': forms.CheckboxInput(attrs={'type': 'checkbox', 'id': 'id_template_is_ativo'}),
        }

        labels = {
            'id': 'ID',
            'tipo_evento': 'Tipo de Evento',
            'id_template': 'Nome do Template',
            'base_text': 'Mensagem',
            'is_ativo': 'Ativo?'
        }