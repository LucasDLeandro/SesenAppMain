from django import forms
from datetime import datetime

from ..models.elev_so_model import *

class ElevCreateOsForm(forms.ModelForm):
    aprisionamento = forms.ChoiceField(
        label='Houve Aprisionamento?',
        choices=[('', 'Não Informada'),
                 ('True', 'Sim'),
                 ('False', 'Não'),
                ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    alarme_ems = forms.CharField(
        label='Alarme EMS',
        required=False,
        widget=forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '200', 'placeholder': 'Informe o Alarme EMS'}),
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
            'alarme_ems',
            'elevador_parado',
            'status'
            ]
        
        widgets = {
            'protocolo': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '20', 'placeholder': 'Ex: 123456...', 'required': True}),
            'elevador': forms.Select(attrs={'type': 'select', 'class': 'form-select', 'required': True}),
            'aprisionamento': forms.Select(attrs={'class':'form-select'}),
            'ocorrencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'atendente': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'maxlength': '150'}),
            'solicitante': forms.TextInput(attrs={'type': 'text', 'class': 'form-control', 'required': True}),
            'elevador_parado': forms.Select(attrs={'type': 'select', 'class': 'form-select', 'required': True})
        
        }

        labels = {
            'data_hora': 'Data e Hora da Ocorrência',
            'protocolo': 'Protocolo',
            'elevador': 'Elevador',
            'aprisionamento': 'Elevador parou, causando aprisionamento?',
            'ocorrencia': 'Ocorrência',
            'atendente': 'Atendente',
            'solicitante': 'Solicitante',
            'alarme_ems': 'Alarme EMS',
            'elevador_parado': 'Elevador Parado?',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'elevador_parado' in self.fields:
            self.fields['elevador_parado'].choices = [c for c in STATUS_ELEVADOR_CHOICES if c[0] != 'PROGRAMADO']

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

    houve_substituicao_pecas = forms.ChoiceField(
        label='Houve substituição/necessidade de peças?',
        choices=[
            ('Nao', 'Não houve necessidade'), 
            ('Sim_Imediata', 'Sim, já foi substituída'), 
            ('Sim_Posterior', 'Sim, será substituída posteriormente (Pendente)')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_houve_substituicao_pecas'})
    )

    peca_substituida = forms.CharField(
        label='Qual peça?',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_peca_substituida', 'placeholder': 'Descreva a peça'})
    )

    justificativa_parada = forms.CharField(
        label='Justificativa da Parada',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'id_justificativa_parada', 'rows': 2, 'placeholder': 'Explique por que o elevador continuará parado...'})
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
            'justificativa_parada',
            'status',
        ]
        
        widgets = {
            'id': forms.HiddenInput(),
            'protocolo': forms.TextInput(attrs={'type': 'text', 'id': 'id_protocolo_concluir_os', 'class': 'form-control', 'maxlength': '9', 'readonly': 'readonly'}),
            'tecnico': forms.Select(attrs={'class': 'form-select', 'id': 'concluirTecnicoOS'}),
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


        
        
