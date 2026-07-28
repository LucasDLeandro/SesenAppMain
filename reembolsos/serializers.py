from rest_framework import serializers
from .models import ServidorReembolso, SolicitacaoReembolso, LimiteReembolso, FaturaReembolso, ConfiguracaoRelatorio

class MoedaField(serializers.DecimalField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return super().to_internal_value(data)

class LimiteReembolsoSerializer(serializers.ModelSerializer):
    valor = MoedaField(max_digits=10, decimal_places=2)
    class Meta:
        model = LimiteReembolso
        fields = '__all__'

class ServidorReembolsoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='pessoa.nome', required=False)
    cpf = serializers.CharField(source='pessoa.cpf', required=False)
    
    class Meta:
        model = ServidorReembolso
        fields = '__all__'

    def validate_cpf(self, value):
        if value:
            import re
            value = re.sub(r'\D', '', value)
        return value

    def create(self, validated_data):
        pessoa_data = validated_data.pop('pessoa', {})
        from usuarios.models import Pessoa
        pessoa, _ = Pessoa.objects.get_or_create(
            cpf=pessoa_data.get('cpf'),
            defaults={'nome': pessoa_data.get('nome')}
        )
        validated_data['pessoa'] = pessoa
        return super().create(validated_data)

    def update(self, instance, validated_data):
        pessoa_data = validated_data.pop('pessoa', {})
        if pessoa_data:
            if instance.pessoa:
                if 'nome' in pessoa_data:
                    instance.pessoa.nome = pessoa_data['nome']
                if 'cpf' in pessoa_data:
                    instance.pessoa.cpf = pessoa_data['cpf']
                instance.pessoa.save()
        return super().update(instance, validated_data)

    def validate_telefone_linha(self, value):
        if value:
            import re
            value = re.sub(r'\D', '', value)
            if len(value) in (10, 11) and not value.startswith('55'):
                value = f"55{value}"
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.cargo_limite:
            data['cargo'] = instance.cargo_limite.cargo
            data['teto_ressarcimento'] = str(instance.cargo_limite.valor)
        return data

class FaturaReembolsoSerializer(serializers.ModelSerializer):
    valor_fatura = MoedaField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    valor_servico = MoedaField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    
    class Meta:
        model = FaturaReembolso
        fields = '__all__'
        read_only_fields = ('solicitacao', 'valor_ressarcido')

class SolicitacaoReembolsoSerializer(serializers.ModelSerializer):
    servidor_nome = serializers.CharField(source='servidor.nome', read_only=True)
    faturas = FaturaReembolsoSerializer(many=True, read_only=True)
    
    # Adicionamos as properties como readonly
    valor_ressarcido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    periodo_inicio = serializers.DateField(read_only=True)
    periodo_fim = serializers.DateField(read_only=True)

    class Meta:
        model = SolicitacaoReembolso
        fields = '__all__'

class ConfiguracaoRelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoRelatorio
        fields = '__all__'
