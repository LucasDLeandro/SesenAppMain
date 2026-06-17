from rest_framework import serializers

from decimal import Decimal

from .models import ElevOrderReg

from .utils import calc_hrs_uteis_parado

class ElevRegistrarOsSerializer(serializers.ModelSerializer):
    aprisionamento = serializers.CharField(required=False, allow_null=True, allow_blank=True)
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

    def validate_aprisionamento(self, value):
        print(value)
        if value == '1':
            return True
        elif value == '2':
            return False
        else:
            return None

    

class ElevConcluirOsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElevOrderReg
        fields = [
            'id',
            'protocolo',
            'data_hora_chegada',
            'data_hora_conclusao',
            'tecnico',
            'servico',
            'elevador',
            'elevador_parado',
            'status',
        ]

        read_only_fields = ['id', 'protocolo', 'elevador']
    
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