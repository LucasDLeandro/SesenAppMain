from django import forms
from decimal import Decimal, InvalidOperation
import re


from ..models.model_contratos import Contratos

class Contrato(forms.ModelForm):
    valor = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
    )

    class Meta:
        model = Contratos
        fields = [
            'empresa',
            'cnpj',
            'num_contrato',
            'objeto',
            'valor',
            'inicio_vigencia',
            'termino_vigencia',
            'sei_processo',
            'sei_dod',
            'sei_etp',
            'sei_tr',
            'sei_edital',
            'sei_fiscais',
            'status',
        ]

        labels = {
            'empresa': 'EMPRESA',
            'cnpj': 'CNPJ',
            'num_contrato': 'CONTRATO',
            'objeto': 'OBJETO',
            'valor': 'VALOR',
            'inicio_vigencia': 'Inicio da Vigência',
            'termino_vigencia': 'Termino da Vigência',
            'sei_processo': 'PROCESSO',
            'sei_dod': 'DOD',
            'sei_etp': 'ETP',
            'sei_tr': 'TR',
            'sei_edital': 'EDITAL',
            'sei_fiscais': 'DOC. DESIGNAÇÃO DE FISCAIS',
            'status': 'Status',
        }

        widgets = {
            'empresa': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'num_contrato': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'objeto': forms.Textarea(attrs={'type': 'text', 'class': 'form-control', 'rows': 4}),
            #'valor': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'inicio_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'termino_vigencia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'format': '%d/%m/%Y'}),
            'sei_processo': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'sei_dod': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'sei_etp': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'sei_tr': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'sei_edital': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'sei_fiscais': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'status': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].localize=True

    def clean_num_contrato(self):
        dado = self.cleaned_data.get('num_contrato')
        pattern = r'(\d{1,3}\/\d{2,4})'

        if dado:
            dado_limpo = re.search(pattern, dado)
            if dado_limpo:
                dado = dado_limpo.group(1)
            else:
                raise forms.ValidationError("Insira o número e o ano do contrato. Ex: '10/2025'")
        return dado

    def clean_valor(self):
        dado = self.cleaned_data.get("valor")
        char_list=["R", "$", " "]
        if dado:
            try:
                for c in char_list:
                    dado = dado.replace(c, '')
                dado = dado.replace('.', '').replace(',', '.')
                return Decimal(dado)
            except (ValueError, TypeError, InvalidOperation) as e:
                raise forms.ValidationError(f"Erro: {e} \n Informe o um valor monetário válido.")
        return dado
    
    def clean(self):
        cleaned_data = super().clean()
        pattern = r'(\d{4,7})'

        field_list = [
            'sei_dod',
            'sei_etp',
            'sei_tr',
            'sei_edital',
            'sei_fiscais'
        ]

        for field in field_list:
            valor = self.cleaned_data.get(field)
            if valor:
                valor_limpo = re.search(pattern, valor)
                if valor_limpo:
                    self.cleaned_data[field] = valor_limpo.group(1)
                else:
                    self.cleaned_data[field] = ""

        return cleaned_data
