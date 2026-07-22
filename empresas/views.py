from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from .models import Empresa, ContatoEmpresa
from .serializers import EmpresaSerializer, ContatoEmpresaSerializer
from contratos.models import Contratos
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all().order_by('-id')
    serializer_class = EmpresaSerializer
    pagination_class = None  # Desabilita paginação para evitar problema com DataTable
    permission_classes = [AllowAny]  # Permite acesso sem autenticação

class ContatoEmpresaViewSet(viewsets.ModelViewSet):
    queryset = ContatoEmpresa.objects.all().order_by('-id')
    serializer_class = ContatoEmpresaSerializer
    pagination_class = None  # Desabilita paginação para evitar problema com DataTable
    permission_classes = [AllowAny]  # Permite acesso sem autenticação

def dashboard_empresas(request):
    return render(request, 'empresas/dashboard_empresas.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def get_contatos_por_app(request):
    app = request.query_params.get('app', '')
    if not app:
        return Response([])

    # categoria é JSONField (lista), usar __contains para buscar dentro do array
    contratos = Contratos.objects.filter(categoria__contains=app)
    empresa_ids = contratos.values_list('empresa_id', flat=True).distinct()
    
    contatos = ContatoEmpresa.objects.filter(empresa_id__in=empresa_ids)
    
    # Return list of dicts with nome, cargo, empresa e email
    data = [
        {
            'nome': c.nome_contato,
            'cargo': c.cargo or '',
            'empresa': c.empresa.nome_empresa,
            'email': c.email or '',
            'telefone': c.telefone or '',
        }
        for c in contatos
    ]
    return Response(data)
