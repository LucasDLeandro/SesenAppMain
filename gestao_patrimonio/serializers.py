from rest_framework import serializers
from .models import TransferenciaPatrimonio
from audiovideo.models import TV, EquipamentoAV
from telefonia.models.aparelhos_telefonicos import AparelhoVoip

class MoedaField(serializers.DecimalField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return super().to_internal_value(data)

class TVSerializer(serializers.ModelSerializer):
    valor = MoedaField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    class Meta:
        model = TV
        fields = '__all__'

class AparelhoVoipSerializer(serializers.ModelSerializer):
    class Meta:
        model = AparelhoVoip
        fields = '__all__'

class EquipamentoAVSerializer(serializers.ModelSerializer):
    valor = MoedaField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    class Meta:
        model = EquipamentoAV
        fields = '__all__'

class TransferenciaPatrimonioSerializer(serializers.ModelSerializer):
    equipamento_detalhes = serializers.SerializerMethodField()
    equipamento_id = serializers.IntegerField(write_only=True)
    equipamento_tipo = serializers.CharField(write_only=True)
    
    class Meta:
        model = TransferenciaPatrimonio
        fields = ['id', 'numero_requisicao', 'origem', 'destino', 'data_transferencia', 'responsavel', 'motivo', 'equipamento_detalhes', 'equipamento_id', 'equipamento_tipo']

    def create(self, validated_data):
        eq_id = validated_data.pop('equipamento_id')
        eq_tipo = validated_data.pop('equipamento_tipo')
        
        from django.contrib.contenttypes.models import ContentType
        if eq_tipo == 'telefone':
            ct = ContentType.objects.get_for_model(AparelhoVoip)
        elif eq_tipo == 'av':
            ct = ContentType.objects.get_for_model(EquipamentoAV)
        else:
            ct = ContentType.objects.get_for_model(TV)
            
        validated_data['content_type'] = ct
        validated_data['object_id'] = eq_id
        return super().create(validated_data)

    def get_equipamento_detalhes(self, obj):
        if not obj.equipamento:
            return None
        # Retornar dados unificados pro frontend
        return {
            'id': obj.equipamento.id,
            'marca': getattr(obj.equipamento, 'marca', None),
            'modelo': getattr(obj.equipamento, 'modelo', None),
            'patrimonio': getattr(obj.equipamento, 'patrimonio', None),
        }
