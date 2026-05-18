from django import forms
from datetime import datetime

from ..models.elev_so_model import *

class ElevCreateOsForm(forms.ModelForm):
    data_hoje = datetime.now().strftime('%Y-%m-%d %H:%M')
    aprisionamento = forms.TypedChoiceField(
        label='Houve Aprisionamento?',
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
            'status'
            ]
        
        widgets = {
            'protocolo': forms.TextInput(attrs={'type': 'text', 'id': 'id_protocolo_criar_os', 'class': 'form-control', 'maxlength': '9'}),
            'elevador': forms.Select(attrs={'type': 'select', 'class': 'form-select', 'required': True}),
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

class ElevConcluirOsForm(forms.ModelForm):
    data_agora = datetime.now().strftime('%Y-%m-%d %H:%M')

    data_hora_chegada = forms.DateTimeField(
        label='Data/Hora - Chegada',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local' , 'class': 'form-control'}), 
    )

    data_hora_conclusao = forms.DateTimeField(
        label='Data/Hora - Conclusão',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local' , 'class': 'form-control'}),  
    )

    class Meta:
        model = ElevOrderReg
        fields = [
            'id',
            'protocolo',
            'data_hora_chegada',
            'data_hora_conclusao',
            'tecnico',
            'servico',
            'elevador_parado',
            'status',
        ]
        
        widgets = {
            'id': forms.HiddenInput(),
            'protocolo': forms.TextInput(attrs={'type': 'text', 'id': 'id_protocolo_concluir_os', 'class': 'form-control', 'maxlength': '9', 'readonly': 'readonly'}),
            'tecnico': forms.TextInput(attrs={'type': 'text', 'class': 'form-control'}),
            'servico': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'type': 'select', 'class': 'form-select'}),
            'elevador_parado': forms.Select(attrs={'type': 'select', 'class': 'form-select', 'required': True})
        }

        labels = {
            'id': 'ID - OS',
            'protocolo': 'Protocolo',
            'tecnico': 'Técnico',
            'servico': 'Serviço Executado',
            'elevador_parado': 'Elevador Parado',
            'status': 'Status da OS'
        }



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_hora_chegada'].initial = self.data_agora
        self.fields['data_hora_conclusao'].initial = self.data_agora


        
        
