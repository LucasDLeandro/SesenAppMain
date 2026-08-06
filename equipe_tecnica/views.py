from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tecnico, SolicitacaoAcesso, LiberacaoAcessoDiaria
from .serializers import TecnicoSerializer, SolicitacaoAcessoSerializer, LiberacaoAcessoDiariaSerializer
from .utils import enviar_email_liberacao, montar_email_liberacao
from empresas.models import Empresa

class TecnicoViewSet(viewsets.ModelViewSet):
    queryset = Tecnico.objects.all().order_by('-id')
    serializer_class = TecnicoSerializer

class SolicitacaoAcessoViewSet(viewsets.ModelViewSet):
    queryset = SolicitacaoAcesso.objects.all().order_by('-id')
    serializer_class = SolicitacaoAcessoSerializer

class LiberacaoAcessoDiariaViewSet(viewsets.ModelViewSet):
    queryset = LiberacaoAcessoDiaria.objects.all().order_by('-id')
    serializer_class = LiberacaoAcessoDiariaSerializer

    @action(detail=True, methods=['get'])
    def preview_email(self, request, pk=None):
        liberacao = self.get_object()
        dados = montar_email_liberacao(liberacao)
        dados['email_enviado'] = liberacao.email_enviado
        dados['liberacao_id'] = liberacao.id
        return Response(dados)

    @action(detail=True, methods=['post'])
    def enviar_email(self, request, pk=None):
        liberacao = self.get_object()
        if liberacao.email_enviado:
            return Response(
                {'status': 'Este e-mail já foi enviado anteriormente.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Dados customizados do form
        to_email = request.POST.get('to_email')
        cc_email = request.POST.get('bcc_email') # Note: form might still send as bcc_email or cc_email
        if request.POST.get('cc_email'):
            cc_email = request.POST.get('cc_email')
            
        assunto = request.POST.get('assunto')
        corpo = request.POST.get('corpo')
        anexos = request.FILES.getlist('anexos_externos')

        sucesso = enviar_email_liberacao(
            liberacao.id, 
            custom_to=to_email, 
            custom_cc=cc_email, 
            custom_subject=assunto, 
            custom_body=corpo, 
            anexos=anexos
        )
        
        if sucesso:
            return Response({'status': 'E-mail enviado com sucesso'})
        return Response(
            {'status': 'Falha ao enviar e-mail. Verifique o template e o destinatário configurado.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def dashboard_acessos(request):
    empresas = Empresa.objects.all().order_by('nome_empresa')
    is_admin_or_supervisor = False
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name__in=['Administrador', 'Supervisor']).exists():
            is_admin_or_supervisor = True

    hoje = timezone.now().date()
    
    total_pedidos = SolicitacaoAcesso.objects.count()
    liberacoes_mes = LiberacaoAcessoDiaria.objects.filter(data_inicio__year=hoje.year, data_inicio__month=hoje.month).count()
    tecnicos_mes = LiberacaoAcessoDiaria.objects.filter(data_inicio__year=hoje.year, data_inicio__month=hoje.month).values_list('tecnicos', flat=True).distinct().count()
    agendamentos_pendentes = LiberacaoAcessoDiaria.objects.filter(email_enviado=False, data_agendamento_email__isnull=False).count()

    return render(request, 'equipe_tecnica/dashboard_acessos.html', {
        'empresas': empresas,
        'is_admin_or_supervisor': is_admin_or_supervisor,
        'total_pedidos': total_pedidos,
        'liberacoes_mes': liberacoes_mes,
        'tecnicos_mes': tecnicos_mes,
        'agendamentos_pendentes': agendamentos_pendentes
    })
