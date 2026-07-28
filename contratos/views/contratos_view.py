from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Sum, Count
from rest_framework import status
from django.contrib.auth.decorators import login_required

from ..models.model_contratos import (
    Contratos, ProcessoLicitatorio, MedicaoMensal, Pagamento, 
    TramitacaoSEI, CronogramaContratacao, TermoAditivo, PostoTrabalho,
    ItemCustoExtra, Profissional, AlocacaoProfissional
)
from ..serializers import (
    ContratoSerializer, 
    ProcessoLicitatorioSerializer, 
    MedicaoMensalSerializer, 
    PagamentoSerializer,
    TramitacaoSEISerializer,
    CronogramaContratacaoSerializer,
    TermoAditivoSerializer,
    PostoTrabalhoSerializer,
    ItemCustoExtraSerializer,
    ProfissionalSerializer,
    AlocacaoProfissionalSerializer
)
from ..services.comprasnet_service import ComprasNetService
from empresas.models import Empresa

from rest_framework.decorators import action
from datetime import date, timedelta
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404

class TermoAditivoViewSet(viewsets.ModelViewSet):
    queryset = TermoAditivo.objects.all().order_by('-inicio_vigencia')
    serializer_class = TermoAditivoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        contrato_id = self.request.query_params.get('contrato', None)
        if contrato_id:
            queryset = queryset.filter(contrato_id=contrato_id)
        return queryset

class PostoTrabalhoViewSet(viewsets.ModelViewSet):
    queryset = PostoTrabalho.objects.all().order_by('nome_cargo')
    serializer_class = PostoTrabalhoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        contrato_id = self.request.query_params.get('contrato', None)
        if contrato_id:
            queryset = queryset.filter(contrato_id=contrato_id)
        return queryset

class ItemCustoExtraViewSet(viewsets.ModelViewSet):
    queryset = ItemCustoExtra.objects.all()
    serializer_class = ItemCustoExtraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        contrato_id = self.request.query_params.get('contrato', None)
        if contrato_id:
            queryset = queryset.filter(contrato_id=contrato_id)
        return queryset

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all().order_by('pessoa__nome')
    serializer_class = ProfissionalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super(ProfissionalViewSet, self).create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AlocacaoProfissionalViewSet(viewsets.ModelViewSet):
    queryset = AlocacaoProfissional.objects.all().order_by('-data_inicio')
    serializer_class = AlocacaoProfissionalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        posto_id = self.request.query_params.get('posto', None)
        if posto_id:
            queryset = queryset.filter(posto_id=posto_id)
        contrato_id = self.request.query_params.get('contrato', None)
        if contrato_id:
            queryset = queryset.filter(posto__contrato_id=contrato_id)
        return queryset


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

    def get_queryset(self):
        qs = super().get_queryset()
        app_vinculado = self.request.query_params.get('app_vinculado')
        categoria = self.request.query_params.get('categoria')
        mes = self.request.query_params.get('mes')
        ano = self.request.query_params.get('ano')
        
        if app_vinculado:
            qs = qs.filter(categoria__contains=app_vinculado) # Backward compatibility
        if categoria:
            qs = qs.filter(categoria__contains=categoria)
            
        if mes and ano:
            competencia = f"{mes.zfill(2)}/{ano}"
            # Filtra contratos que possuem medição naquela competência
            qs = qs.filter(medicoes__competencia=competencia).distinct()
            
        return qs

class MedicaoMensalViewSet(viewsets.ModelViewSet):
    queryset = MedicaoMensal.objects.all().order_by('-created_at')
    serializer_class = MedicaoMensalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        medicao = serializer.save(avaliador=self.request.user.username)
        # Create the associated Pagamento based on request data
        data = self.request.data
        Pagamento.objects.create(
            medicao=medicao,
            protocolo_relatorio_mensal=data.get('protocolo_relatorio_mensal', ''),
            protocolo_imr=data.get('protocolo_imr', ''),
            protocolo_trd_trt=data.get('protocolo_trd_trt', ''),
            protocolo_nf=data.get('protocolo_nf', ''),
            protocolo_nota_tecnica=data.get('protocolo_nota_tecnica', ''),
            valor_faturado=data.get('valor_faturado') or '0.00',
            porcentagem_glosa=data.get('porcentagem_glosa') or '0.00',
            porcentagem_multa=data.get('porcentagem_multa') or '0.00',
            status='PENDENTE'
        )

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all().order_by('-created_at')
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    from datetime import date
    
    contrato_id = request.query_params.get('contrato_id')
    mes = request.query_params.get('mes')
    ano = request.query_params.get('ano')
    
    # Defaults se mes e ano não estiverem presentes (Mês atual)
    hoje = date.today()
    filtro_mes = mes if mes else str(hoje.month).zfill(2)
    filtro_ano = ano if ano else str(hoje.year)
    competencia = f"{filtro_mes.zfill(2)}/{filtro_ano}"

    qs_contratos = Contratos.objects.filter(status='VIGENTE')
    qs_pagamentos = Pagamento.objects.all()
    
    if contrato_id:
        qs_contratos = qs_contratos.filter(id=contrato_id)
        qs_pagamentos = qs_pagamentos.filter(medicao__contrato_id=contrato_id)
        
    # Valor Total dos Contratos (Global ou filtrado por contrato_id)
    valor_total = qs_contratos.aggregate(total=Sum('valor'))['total'] or 0
    
    # Valor Mensal Estimado
    valor_estimado = qs_contratos.aggregate(total=Sum('valor_mensal_estimado'))['total'] or 0

    # Valor Pago no Mês (usando a competência)
    qs_pagamentos_mes = qs_pagamentos.filter(medicao__competencia=competencia)
    valor_pago = qs_pagamentos_mes.aggregate(total=Sum('valor_pago'))['total'] or 0

    # Glosas e Multas no Mês
    glosas_multas = qs_pagamentos_mes.aggregate(
        glosas=Sum('valor_glosa'),
        multas=Sum('valor_multa')
    )
    total_descontos = (glosas_multas['glosas'] or 0) + (glosas_multas['multas'] or 0)

    # Próximos contratos a vencer
    proximos_vencer = qs_contratos.filter(
        termino_vigencia__gte=hoje
    ).order_by('termino_vigencia')[:5]
    
    vencimentos_lista = [
        {
            'id': c.id,
            'num_contrato': c.num_contrato,
            'empresa': c.empresa.nome_empresa if c.empresa else '',
            'termino_vigencia': c.termino_vigencia.strftime('%Y-%m-%d') if c.termino_vigencia else None
        } for c in proximos_vencer
    ]
    
    # Gráfico Visão Geral (Últimos 6 meses)
    # Pega o mês/ano filtrado e volta 5 meses.
    mes_int = int(filtro_mes)
    ano_int = int(filtro_ano)
    
    chart_categories = []
    chart_estimado = []
    chart_medido = []
    
    meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    for i in range(5, -1, -1):
        m = mes_int - i
        a = ano_int
        if m <= 0:
            m += 12
            a -= 1
        comp = f"{str(m).zfill(2)}/{a}"
        chart_categories.append(meses_nomes[m-1])
        
        # O valor estimado é constante para o gráfico se não houve aditivo, 
        # mas vamos simplificar usando o valor estimado atual:
        chart_estimado.append(float(valor_estimado))
        
        val_medido = qs_pagamentos.filter(medicao__competencia=comp).aggregate(total=Sum('valor_faturado'))['total'] or 0
        chart_medido.append(float(val_medido))

    return Response({
        'valor_total_contratos': valor_total,
        'valor_estimado': valor_estimado,
        'valor_pago': valor_pago,
        'total_glosas': total_descontos,
        'proximos_vencer': vencimentos_lista,
        'chart_data': {
            'categories': chart_categories,
            'estimado': chart_estimado,
            'medido': chart_medido
        }
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

@login_required
def pagamentos_view(request):
    return render(request, 'contratos/pagamentos.html')

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_contratos_comprasnet(request):
    """
    Busca os contratos ativos no Comprasnet (UG 070001).
    """
    contratos = ComprasNetService.obter_contratos_ativos_ug()
    return Response(contratos)

@login_required
def visao_geral_contrato(request, pk):
    contrato = get_object_or_404(Contratos, pk=pk)
    return render(request, 'contratos/visao_geral_contrato.html', {
        'contrato': contrato
    })