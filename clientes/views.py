from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Sum, Count
from .models import Cliente, Pedido
from .serializers import ClienteSerializer, PedidoSerializer
import json

# ===========================
# HTML VIEWS (Frontend)
# ===========================

def clientes_view(request):
    """View padrão de listagem de clientes."""
    clientes = Cliente.objects.all().order_by('-criado_em')
    return render(request, 'clientes/clientes_list.html', {'clientes': clientes})

def dashboard_view(request):
    """View do dashboard de desempenho."""
    # Métricas gerais
    total_pedidos = Pedido.objects.count()
    total_valor = Pedido.objects.aggregate(total=Sum('valor'))['total'] or 0
    total_clientes = Cliente.objects.count()

    # Desempenho por tipo de cliente (Gráfico de Pizza)
    clientes_por_tipo = Cliente.objects.values('tipo').annotate(total=Count('id'))
    tipos_labels = [c['tipo'] for c in clientes_por_tipo]
    tipos_data = [c['total'] for c in clientes_por_tipo]

    # Valor dos pedidos por cliente (Gráfico de Barras)
    pedidos_por_cliente = Cliente.objects.annotate(valor_total=Sum('pedidos__valor')).filter(valor_total__isnull=False)
    clientes_labels = [c.nome for c in pedidos_por_cliente]
    valores_data = [float(c.valor_total) for c in pedidos_por_cliente]

    context = {
        'total_pedidos': total_pedidos,
        'total_valor': float(total_valor),
        'total_clientes': total_clientes,
        'tipos_labels': json.dumps(tipos_labels),
        'tipos_data': json.dumps(tipos_data),
        'clientes_labels': json.dumps(clientes_labels),
        'valores_data': json.dumps(valores_data),
    }

    return render(request, 'clientes/dashboard.html', context)


# ===========================
# API VIEWSETS (REST Framework)
# ===========================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

