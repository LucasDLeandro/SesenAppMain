from django import forms
from datetime import datetime

from ..models.elevadores_reg_os_model import *

class CreateOsForm(forms.ModelForm):
    data_hoje = datetime.now().strftime('%Y-%m-%dT%H:%M')
    aprisionamento = forms.TypedChoiceField(
        label='Elevador parou, causando aprisionamento?',
        choices=[(1, 'Não Informado'),
                 (2, 'Sim'),
                 (3, 'Não'),
                ],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    data_hora = forms.DateTimeField(
        label='Data e Hora da Ocorrência',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local' , 'class': 'form-control'}),
        
    )

    class Meta:
        model = ElevOrderReg
        fields = [
            'data_hora',
            'protocolo',
            'elevador',
            'aprisionamento',
            'ocorrencia',
            'atendente',
            'solicitante',
            'elevador_parado',
            ]
        
        widgets = {
            'protocolo': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '9'}),
            'elevador': forms.Select(attrs={'type': 'select', 'class': 'form-select'}),
            'elevador': forms.Select(attrs={'class': 'form-select'}),
            'aprisionamento': forms.Select(attrs={'class':'form-select'}),
            'ocorrencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'atendente': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '150'}),
            'solicitante': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'elevador_parado': forms.Select(attrs={'type': 'select', 'class': 'form-select'})
        
        }

        labels = {
            'data_hora': 'Data e Hora da Ocorrência',
            'protocolo': 'Protocolo',
            'elevador': 'Elevador',
            'aprisionamento': 'Elevador parou, causando aprisionamento?',
            'ocorrencia': 'Ocorrência',
            'atendente': 'Atendente',
            'solicitante': 'Solicitante',
            'elevador_parado': 'Elevador Parado?',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Configura valores iniciais para os campos do Formulário
        self.fields['data_hora'].initial = self.data_hoje
        

    def clean_aprisionamento(self):
        value = self.cleaned_data['aprisionamento']

        if value == 1:
            return True
        elif value == 2:
            return False
        else:
            return None

        
        
