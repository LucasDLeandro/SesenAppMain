from rest_framework import serializers
from .models import Cliente, Pedido

class ClienteSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'tipo', 'tipo_display', 'criado_em', 'atualizado_em']


class PedidoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'cliente_nome', 'descricao', 'valor', 'status', 'status_display', 'data_pedido']
