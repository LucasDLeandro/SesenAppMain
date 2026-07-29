from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ProcessoSEI, HistoricoAndamento
from .sei_client import SeiClient
from datetime import datetime

class ProcessoSEISerializer(serializers.ModelSerializer):
    contrato_nome = serializers.CharField(source='contrato.numero_contrato', read_only=True)
    empresa_nome = serializers.CharField(source='empresa.nome_empresa', read_only=True)

    class Meta:
        model = ProcessoSEI
        fields = '__all__'

class ProcessoSEIViewSet(viewsets.ModelViewSet):
    queryset = ProcessoSEI.objects.all()
    serializer_class = ProcessoSEISerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='sincronizar')
    def sincronizar(self, request, pk=None):
        processo = self.get_object()
        client = SeiClient()
        
        # Como as credenciais ainda não estão setadas, vamos apenas fingir um sucesso
        # Quando configurado, a chamada seria client.get_processo_info e client.get_andamentos
        
        processo.save() # Atualiza apenas o timestamp ultima_sincronizacao no save
        
        return Response({"status": "sincronizado", "mensagem": "Sincronização acionada com sucesso (Mock)."})

class DashboardSEIView(TemplateView):
    template_name = 'monitoramento_sei/dashboard_sei.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        processos = ProcessoSEI.objects.all()
        
        context['prioritarios'] = processos.filter(tipo='PRIORITARIO').order_by('tempo_tramitacao')
        context['em_tramite'] = processos.filter(tipo='TRAMITE').order_by('tempo_tramitacao')
        context['concluidos'] = processos.filter(tipo='CONCLUIDO').order_by('-updated_at')
        return context
