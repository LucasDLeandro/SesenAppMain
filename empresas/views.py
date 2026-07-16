from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from .models import Empresa, ContatoEmpresa
from .serializers import EmpresaSerializer, ContatoEmpresaSerializer

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
