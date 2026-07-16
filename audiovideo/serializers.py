from rest_framework import serializers
from .models import EventoAV, OrdemServicoAV
from gestao_patrimonio.serializers import EquipamentoAVSerializer

class EventoAVSerializer(serializers.ModelSerializer):
    # To display equipment names in event JSON:
    equipamentos_detalhes = EquipamentoAVSerializer(source='equipamentos_alocados', many=True, read_only=True)
    
    class Meta:
        model = EventoAV
        fields = '__all__'

class OrdemServicoAVSerializer(serializers.ModelSerializer):
    equipamento_detalhes = EquipamentoAVSerializer(source='equipamento', read_only=True)
    
    class Meta:
        model = OrdemServicoAV
        fields = '__all__'
