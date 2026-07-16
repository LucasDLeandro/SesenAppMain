from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, views
from rest_framework.response import Response

from audiovideo.models import TV, EquipamentoAV
from telefonia.models.aparelhos_telefonicos import AparelhoVoip
from .models import TransferenciaPatrimonio
from .serializers import TVSerializer, AparelhoVoipSerializer, EquipamentoAVSerializer, TransferenciaPatrimonioSerializer

@login_required
def dashboard_transferencias(request):
    return render(request, 'gestao_patrimonio/dashboard.html')

class EquipamentoBaseView(views.APIView):
    def get(self, request, *args, **kwargs):
        data = []
        for eq in AparelhoVoip.objects.all():
            data.append({'id': eq.id, 'marca': 'Telefone', 'modelo': eq.modelo, 'patrimonio': eq.patrimonio, 'type': 'telefone'})
        for eq in EquipamentoAV.objects.all():
            data.append({'id': eq.id, 'marca': eq.marca, 'modelo': eq.modelo, 'patrimonio': eq.patrimonio, 'type': 'av'})
        for eq in TV.objects.all():
            data.append({'id': eq.id, 'marca': eq.marca, 'modelo': eq.modelo, 'patrimonio': eq.patrimonio, 'type': 'tv'})
        return Response(data)

class TVViewSet(viewsets.ModelViewSet):
    queryset = TV.objects.all().order_by('-id')
    serializer_class = TVSerializer

class AparelhoTelefonicoViewSet(viewsets.ModelViewSet):
    queryset = AparelhoVoip.objects.all().order_by('-id')
    serializer_class = AparelhoVoipSerializer

class EquipamentoAVViewSet(viewsets.ModelViewSet):
    queryset = EquipamentoAV.objects.all().order_by('-id')
    serializer_class = EquipamentoAVSerializer
    
    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super().create(request, *args, **kwargs)
        
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class TransferenciaPatrimonioViewSet(viewsets.ModelViewSet):
    queryset = TransferenciaPatrimonio.objects.all().order_by('-data_transferencia')
    serializer_class = TransferenciaPatrimonioSerializer
