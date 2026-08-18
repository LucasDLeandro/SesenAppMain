from rest_framework import serializers
from .models import TelefoneSolicitacao, RemessaManutencao, CriarSenha, ContratoColaborador, EmprestimoEvento, TelefoneSolicitacaoAnexo, NadaConsta

class EmprestimoEventoSerializer(serializers.ModelSerializer):
    aparelhos_detalhes = serializers.SerializerMethodField()

    class Meta:
        model = EmprestimoEvento
        fields = '__all__'

    def get_aparelhos_detalhes(self, obj):
        return [
            {
                'id': a.id,
                'patrimonio': a.patrimonio,
                'modelo': a.modelo,
                'mac_address': a.mac_address
            }
            for a in obj.aparelhos.all()
        ]

class TelefoneSolicitacaoAnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelefoneSolicitacaoAnexo
        fields = '__all__'

class TelefoneSolicitacaoSerializer(serializers.ModelSerializer):
    aparelhos_detalhes = serializers.SerializerMethodField()
    ultima_atualizacao = serializers.SerializerMethodField()
    anexos = TelefoneSolicitacaoAnexoSerializer(many=True, read_only=True)

    class Meta:
        model = TelefoneSolicitacao
        fields = '__all__'

    def get_aparelhos_detalhes(self, obj):
        return [
            {
                'patrimonio': a.patrimonio,
                'sala': a.sala,
                'ramal': a.ramal
            }
            for a in obj.aparelhos.all()
        ]

    def get_ultima_atualizacao(self, obj):
        from logs.models import SystemLog
        from django.contrib.contenttypes.models import ContentType
        from django.utils.timezone import localtime
        ct = ContentType.objects.get_for_model(obj)
        log = SystemLog.objects.filter(content_type=ct, object_id=str(obj.pk)).first()
        if log:
            nome = log.user.first_name or log.user.username if log.user else 'Sistema'
            local_time = localtime(log.timestamp) if log.timestamp else None
            data = local_time.strftime('%d/%m/%Y às %H:%M') if local_time else ''
            return f"Atualizado por {nome} em {data}"
        return "Nenhuma atualização registrada"
class RemessaManutencaoSerializer(serializers.ModelSerializer):
    aparelhos = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = RemessaManutencao
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Adicionar detalhes dos aparelhos para a tabela do frontend
        representation['aparelhos_detalhes'] = [
            {'patrimonio': ap.patrimonio, 'modelo': ap.modelo} 
            for ap in instance.aparelhos_manutencao.all()
        ]
        return representation


class CriarSenhaSerializer(serializers.ModelSerializer):
    usuario = serializers.ReadOnlyField()
    class Meta:
        model = CriarSenha
        fields = '__all__'
        extra_kwargs = {
            'protocolo': {'validators': []}
        }


class ContratoColaboradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoColaborador
        fields = '__all__'

class NadaConstaSerializer(serializers.ModelSerializer):
    ramal_vinculado_display = serializers.SerializerMethodField()

    class Meta:
        model = NadaConsta
        fields = '__all__'

    def get_ramal_vinculado_display(self, obj):
        if obj.senha_vinculada and obj.senha_vinculada.ramal:
            return obj.senha_vinculada.ramal
        return 'Não identificado'

