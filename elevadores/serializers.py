from rest_framework import serializers

from decimal import Decimal

from .models import ElevOrderReg

from .utils import calc_hrs_uteis_parado

class ElevRegistrarOsSerializer(serializers.ModelSerializer):
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
            'elevador_parado',
            'status',
        ]

        read_only_fields = ['id', 'protocolo']
    
    def update(self, instance, validated_data):
        abertura = instance.data_hora
        conclusao = validated_data.get('data_hora_conclusao', instance.data_hora_conclusao)

        elev_parado = instance.elevador_parado

        if elev_parado == 'PARADO':
            tmp_parado = calc_hrs_uteis_parado(abertura, conclusao)
            instance.tempo_parado = Decimal(str(tmp_parado))
        else: 
            instance.tempo_parado = Decimal(str(0.0))
        
        instance.data_hora_conclusao = conclusao
        instance.save()

        return instance