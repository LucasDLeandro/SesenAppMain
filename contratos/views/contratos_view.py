from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count

from ..models.model_contratos import Contratos, ProcessoLicitatorio, MedicaoMensal, Pagamento, TramitacaoSEI, CronogramaContratacao
from ..serializers import (
    ContratoSerializer, 
    ProcessoLicitatorioSerializer, 
    MedicaoMensalSerializer, 
    PagamentoSerializer,
    TramitacaoSEISerializer,
    CronogramaContratacaoSerializer
)
from empresas.models import Empresa

from rest_framework.decorators import action
from datetime import date, timedelta
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

class ProcessoLicitatorioViewSet(viewsets.ModelViewSet):
    queryset = ProcessoLicitatorio.objects.all().order_by('-created_at')
    serializer_class = ProcessoLicitatorioSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='gerar-cronograma')
    def gerar_cronograma(self, request, pk=None):
        processo = self.get_object()
        
        # Define os prazos baseados na prioridade (em dias)
        prazos = {
            'BAIXA': {'ETP': 30, 'TR': 30, 'PESQUISA': 15, 'JURIDICO': 20, 'EDITAL': 15},
            'MEDIA': {'ETP': 20, 'TR': 20, 'PESQUISA': 10, 'JURIDICO': 15, 'EDITAL': 10},
            'ALTA': {'ETP': 10, 'TR': 10, 'PESQUISA': 5, 'JURIDICO': 7, 'EDITAL': 5},
            'URGENTE': {'ETP': 5, 'TR': 5, 'PESQUISA': 3, 'JURIDICO': 5, 'EDITAL': 3},
        }
        
        prioridade = processo.prioridade or 'MEDIA'
        tempos = prazos.get(prioridade, prazos['MEDIA'])
        
        # Apaga o cronograma antigo se existir
        processo.cronogramas.all().delete()
        
        hoje = date.today()
        dias_acumulados = 0
        
        for fase in ['ETP', 'TR', 'PESQUISA', 'JURIDICO', 'EDITAL']:
            dias = tempos[fase]
            dias_acumulados += dias
            prazo = hoje + timedelta(days=dias_acumulados)
            
            CronogramaContratacao.objects.create(
                contratacao=processo,
                fase_artefato=fase,
                prazo_entrega=prazo
            )
            
        return Response({'status': 'Cronograma gerado com sucesso'})

    @action(detail=True, methods=['put'], url_path='atualizar-cronograma')
    def atualizar_cronograma(self, request, pk=None):
        processo = self.get_object()
        dados = request.data.get('cronograma', [])
        
        for item in dados:
            fase = item.get('fase_artefato')
            if not fase:
                continue
                
            crono, created = CronogramaContratacao.objects.get_or_create(
                contratacao=processo,
                fase_artefato=fase,
                defaults={'prazo_entrega': item.get('prazo_entrega') or date.today()}
            )
            
            # Atualiza os valores
            if item.get('prazo_entrega'):
                crono.prazo_entrega = item.get('prazo_entrega')
            
            if item.get('data_entrega_real'):
                crono.data_entrega_real = item.get('data_entrega_real')
            else:
                crono.data_entrega_real = None
                
            crono.save()
            
        return Response({'status': 'Cronograma atualizado com sucesso'})

class TramitacaoSEIViewSet(viewsets.ModelViewSet):
    queryset = TramitacaoSEI.objects.all().order_by('-created_at')
    serializer_class = TramitacaoSEISerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(atualizado_por=self.request.user)

    def perform_update(self, serializer):
        serializer.save(atualizado_por=self.request.user)

class CronogramaContratacaoViewSet(viewsets.ModelViewSet):
    queryset = CronogramaContratacao.objects.all().order_by('-created_at')
    serializer_class = CronogramaContratacaoSerializer
    permission_classes = [IsAuthenticated]

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contratos.objects.all().order_by('-created_at')
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

class MedicaoMensalViewSet(viewsets.ModelViewSet):
    queryset = MedicaoMensal.objects.all().order_by('-created_at')
    serializer_class = MedicaoMensalSerializer
    permission_classes = [IsAuthenticated]

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all().order_by('-created_at')
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    # Quantidade de Contratos Ativos
    total_ativos = Contratos.objects.filter(status='VIGENTE').count()
    
    # Valor Total Mensal Estimado (Contratos Ativos)
    valor_estimado = Contratos.objects.filter(status='VIGENTE').aggregate(
        total=Sum('valor_mensal_estimado')
    )['total'] or 0

    # Valor Total Medido no Mês Atual (vamos pegar as últimas medições)
    # Para simplificar, pegamos o total de todas as medições ou podemos agrupar.
    # Como não temos um filtro de mês exato aqui sem saber o formato de 'competencia', 
    # vamos trazer o total geral medido.
    total_medido = MedicaoMensal.objects.aggregate(total=Sum('valor_medido'))['total'] or 0

    # Total de Glosas e Multas aplicadas
    glosas_multas = Pagamento.objects.aggregate(
        glosas=Sum('valor_glosa'),
        multas=Sum('valor_multa')
    )
    total_glosas = glosas_multas['glosas'] or 0
    total_multas = glosas_multas['multas'] or 0

    # Processos Licitatórios
    processos = ProcessoLicitatorio.objects.values('fase').annotate(total=Count('id'))
    
    processos_dict = {
        'PREVISTA': 0,
        'EM_ANDAMENTO': 0,
        'FINALIZADA': 0,
        'SUSPENSA': 0,
        'PLANEJAMENTO': 0,
        'SELECAO': 0,
        'CONCLUIDO': 0,
        'CANCELADO': 0
    }
    for p in processos:
        fase = p['fase']
        if fase in processos_dict:
            processos_dict[fase] = p['total']

    # Próximos contratos a vencer (em 90 dias ou menos, mas vamos pegar os 5 próximos pela data de término)
    from datetime import date
    proximos_vencer = Contratos.objects.filter(
        status='VIGENTE', 
        termino_vigencia__gte=date.today()
    ).order_by('termino_vigencia')[:5]

    proximos_vencer_data = [
        {
            'num_contrato': c.num_contrato,
            'empresa': c.empresa.nome_empresa,
            'termino_vigencia': c.termino_vigencia.isoformat(),
            'valor': c.valor
        } for c in proximos_vencer
    ]

    return Response({
        'total_ativos': total_ativos,
        'valor_estimado': valor_estimado,
        'total_medido': total_medido,
        'total_glosas': total_glosas,
        'total_multas': total_multas,
        'processos_planejamento': processos_dict['PLANEJAMENTO'] + processos_dict['PREVISTA'],
        'processos_selecao': processos_dict['SELECAO'] + processos_dict['EM_ANDAMENTO'],
        'proximos_vencer': proximos_vencer_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_contratacoes_metrics(request):
    total_processos = ProcessoLicitatorio.objects.exclude(fase__in=['CANCELADO', 'CONCLUIDO', 'FINALIZADA']).count()
    valor_estimado_total = ProcessoLicitatorio.objects.exclude(fase__in=['CANCELADO', 'CONCLUIDO', 'FINALIZADA']).aggregate(total=Sum('valor_previsto'))['total'] or 0
    no_pac = ProcessoLicitatorio.objects.filter(esta_no_pac=True).count()
    
    # Processos atrasados (com base no cronograma em que a data_entrega_real é nula e o prazo passou)
    from datetime import date
    from ..models.model_contratos import CronogramaContratacao
    
    atrasados = CronogramaContratacao.objects.filter(
        data_entrega_real__isnull=True, 
        prazo_entrega__lt=date.today()
    ).values('contratacao').distinct().count()

    return Response({
        'total_processos': total_processos,
        'valor_estimado_total': valor_estimado_total,
        'no_pac': no_pac,
        'atrasados': atrasados
    })


def home_contratos(request):
    return render(request, 'contratos/home_contratos.html')

def dashboard_contratos(request):
    empresas = Empresa.objects.all().order_by('nome_empresa')
    processos = ProcessoLicitatorio.objects.all().order_by('-created_at')
    return render(request, 'contratos/dashboard_contratos.html', {
        'empresas': empresas,
        'processos': processos
    })

def dashboard_contratacoes(request):
    processos = ProcessoLicitatorio.objects.all().order_by('-created_at')
    return render(request, 'contratos/dashboard_contratacoes.html', {'processos': processos})