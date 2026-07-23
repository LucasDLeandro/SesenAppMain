from rest_framework import serializers

from decimal import Decimal

from .models import ElevOrderReg
from .models.elev_so_model import AlarmeEmsEvent, ElevadorParadaHistorico

from .utils import calc_hrs_uteis_parado

class ElevRegistrarOsSerializer(serializers.ModelSerializer):
    aprisionamento = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = ElevOrderReg
        fields = [
            'data_hora',
            'protocolo',
            'elevador',
            'tipo_chamado',
            'aprisionamento',
            'ocorrencia',
            'atendente',
            'solicitante',
            'alarme_ems',
            'elevador_parado',
            'status',
            'midia'
        ]

    def validate_aprisionamento(self, value):
        if value == 'True':
            return True
        elif value == 'False':
            return False
        return None

    

class ElevConcluirOsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevOrderReg
        fields = [
            'id',
            'protocolo',
            'tipo_chamado',
            'data_hora_chegada',
            'data_hora_conclusao',
            'tecnico',
            'servico',
            'elevador',
            'elevador_parado',
            'justificativa_parada',
            'status',
            'midia'
        ]

        read_only_fields = ['id', 'protocolo', 'elevador', 'tipo_chamado']
    
    def update(self, instance, validated_data):
        elev_parado = instance.elevador_parado
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        abertura = instance.data_hora
        conclusao = instance.data_hora_conclusao


        if elev_parado == 'PARADO':
            tmp_parado = calc_hrs_uteis_parado(abertura, conclusao)
            instance.tempo_parado = Decimal(str(tmp_parado))
        else: 
            instance.tempo_parado = Decimal(str(0.0))
        
        instance.save()
        return instance

class DashboardFiltroSerializer(serializers.Serializer):
    inicio = serializers.DateTimeField(required=False)
    fim = serializers.DateTimeField(required=False)
    ano = serializers.IntegerField(required=False)
    mes = serializers.IntegerField(required=False)
    dia = serializers.IntegerField(required=False)
    elev = serializers.CharField(required=False)

class AlarmeEmsEventSerializer(serializers.ModelSerializer):
    elevador_display = serializers.CharField(source='get_elevador_display', read_only=True)
    
    class Meta:
        model = AlarmeEmsEvent
        fields = '__all__'

class ElevadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevOrderReg
        fields = "__all__"

from .models import ManutencaoPreventiva, PecaManutencao

class ManutencaoPreventivaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManutencaoPreventiva
        fields = '__all__'

class PecaManutencaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PecaManutencao
        fields = '__all__'

class ElevadorParadaHistoricoSerializer(serializers.ModelSerializer):
    elevador_display = serializers.CharField(source='get_elevador_display', read_only=True)

    class Meta:
        model = ElevadorParadaHistorico
        fields = '__all__'