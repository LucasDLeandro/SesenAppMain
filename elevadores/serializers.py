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

from .models.elev_so_model import RegistroElevadorPreventiva

class RegistroElevadorPreventivaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroElevadorPreventiva
        fields = '__all__'
        read_only_fields = ['manutencao']

class ManutencaoPreventivaSerializer(serializers.ModelSerializer):
    elevadores_registrados = RegistroElevadorPreventivaSerializer(many=True, required=False)
    
    class Meta:
        model = ManutencaoPreventiva
        fields = '__all__'

    def create(self, validated_data):
        elevadores_data = validated_data.pop('elevadores_registrados', [])
        manutencao = super().create(validated_data)
        for elev_data in elevadores_data:
            RegistroElevadorPreventiva.objects.create(manutencao=manutencao, **elev_data)
        return manutencao

    def update(self, instance, validated_data):
        elevadores_data = validated_data.pop('elevadores_registrados', None)
        instance = super().update(instance, validated_data)
        
        if elevadores_data is not None:
            instance.elevadores_registrados.all().delete()
            for elev_data in elevadores_data:
                RegistroElevadorPreventiva.objects.create(manutencao=instance, **elev_data)
                
        return instance


class PecaManutencaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PecaManutencao
        fields = '__all__'

class ElevadorParadaHistoricoSerializer(serializers.ModelSerializer):
    elevador_display = serializers.CharField(source='get_elevador_display', read_only=True)

    class Meta:
        model = ElevadorParadaHistorico
        fields = '__all__'