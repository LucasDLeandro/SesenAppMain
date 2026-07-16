from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EventoAV, OrdemServicoAV
from .serializers import EventoAVSerializer, OrdemServicoAVSerializer

@login_required
def dashboard_audiovideo(request):
    return render(request, 'audiovideo/dashboard.html')

class EventoAVViewSet(viewsets.ModelViewSet):
    queryset = EventoAV.objects.all().order_by('-data_inicio')
    serializer_class = EventoAVSerializer
    
    @action(detail=True, methods=['patch'])
    def concluir(self, request, pk=None):
        evento = self.get_object()
        relatorio = request.data.get('relatorio_conclusao', '')
        
        # Altera o status do evento e salva o relatório
        evento.status = 'concluido'
        evento.relatorio_conclusao = relatorio
        evento.save()
        
        # Libera os equipamentos alocados
        for eq in evento.equipamentos_alocados.all():
            if eq.status == 'alocado':
                eq.status = 'disponivel'
                eq.save()
                
        return Response({'status': 'Evento concluído com sucesso e equipamentos liberados.'})

class OrdemServicoAVViewSet(viewsets.ModelViewSet):
    queryset = OrdemServicoAV.objects.all().order_by('-data_abertura')
    serializer_class = OrdemServicoAVSerializer
