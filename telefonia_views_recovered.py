from django.shortcuts import render

# Create your views here.

from .models import TelefoneSolicitacao, RemessaManutencao, CriarSenha, AparelhoManutencao, ContratoColaborador
from .serializers import TelefoneSolicitacaoSerializer, RemessaManutencaoSerializer, CriarSenhaSerializer, ContratoColaboradorSerializer
from gestao_patrimonio.models import AparelhoTelefonico
# VIEWS TRADICIONAIS (TEMPLATES)
def main_telefonia(request):
    """
    Renderiza a tela principal de telefonia que irá conter os modais HTML puros.
    Toda a submissão e carregamento de dados será gerida via JS + DRF.
    """
    
    # Cálculos para a Dashboard
    from django.db.models import Q
    aparelhos_disponiveis = AparelhoTelefonico.objects.filter(status='estoque', integridade='funciona').count()
    aparelhos_instalados = AparelhoTelefonico.objects.filter(status='instalado').count()
    aparelhos_defeituosos = AparelhoTelefonico.objects.filter(status='defeituoso').count()
    aparelhos_manutencao = AparelhoTelefonico.objects.filter(status='manutencao').count()
    
    solicitacoes_pendentes = TelefoneSolicitacao.objects.exclude(status='concluida').count()
    solicitacoes_concluidas = TelefoneSolicitacao.objects.filter(status='concluida').count()
    
    remessas_total = RemessaManutencao.objects.count()
    total_senhas = CriarSenha.objects.count()
    
    context = {
        'aparelhos_disponiveis': aparelhos_disponiveis,
        'aparelhos_instalados': aparelhos_instalados,
        'aparelhos_defeituosos': aparelhos_defeituosos,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'solicitacoes_concluidas': solicitacoes_concluidas,
        'remessas_total': remessas_total,
    }
    
    return render(request, 'telefonia/main_telefonia.html', context)


from django.http import JsonResponse
from django.db.models import Count

def dashboard_stats(request):
    """Retorna dados estatísticos para os gráficos da telefonia"""
    
    # Status das solicitações
    solicitacoes_status = TelefoneSolicitacao.objects.values('status').annotate(total=Count('id'))
    
    # Aparelhos por status
    aparelhos_status = AparelhoVoip.objects.values('status').annotate(total=Count('id'))
    
    # Senhas por categoria
    senhas_categoria = CriarSenha.objects.values('categoria').annotate(total=Count('id'))
    
    return JsonResponse({
        'solicitacoes': list(solicitacoes_status),
        'aparelhos': list(aparelhos_status),
        'senhas': list(senhas_categoria)
    })

        # Atualiza o agrupado
        if ramais_agrupados:
            solicitacao.ramal = ", ".join(ramais_agrupados)
        if locais_agrupados:
            solicitacao.local = ", ".join(locais_agrupados)
            
        solicitacao.save()
        
        return Response({'status': 'Solicitação concluída com sucesso.'}, status=status.HTTP_200_OK)

class RemessaManutencaoViewSet(viewsets.ModelViewSet):
    queryset = RemessaManutencao.objects.all().order_by('-data_remessa')
    serializer_class = RemessaManutencaoSerializer

    def create(self, request, *args, **kwargs):
        # O serializer validará os campos, incluindo a lista de IDs de aparelhos enviada como write_only
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        aparelhos_ids = serializer.validated_data.pop('aparelhos', [])
        
        # Salva a remessa
        remessa = serializer.save()
        
        # Para cada ID, migra da tabela AparelhoVoip para AparelhoManutencao
        for ap_id in aparelhos_ids:
            try:
                ap_voip = AparelhoVoip.objects.get(id=ap_id)
                # Cria a cópia na nova tabela
                AparelhoManutencao.objects.create(
                    remessa=remessa,
                    patrimonio=ap_voip.patrimonio,
                    modelo=ap_voip.modelo,
                    fcn=ap_voip.fcn,
                    mac_address=ap_voip.mac_address,
                    ramal=ap_voip.ramal,
                    sala=ap_voip.sala,
                    integridade=ap_voip.integridade,
                    status=ap_voip.status,
                )
                # Deleta o original
                ap_voip.delete()
            except AparelhoVoip.DoesNotExist:
                continue
                
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

def gerar_pdf_remessa(request, pk):
    try:
        remessa = RemessaManutencao.objects.get(pk=pk)
    except RemessaManutencao.DoesNotExist:
        return HttpResponse("Remessa não encontrada", status=404)

    enviar_email_boas_vindas_async(senha_obj)
    return JsonResponse({"message": "E-mail enviado com sucesso!"})
    
from .models.padrao_senha import PadraoSenhaTelefonia

def get_pdf_senha_bytes(senha_id):
    try:
        senha = CriarSenha.objects.get(pk=senha_id)
    except CriarSenha.DoesNotExist:
        return None

    padrao = PadraoSenhaTelefonia.objects.filter(ativo=True).first()
    context = {
        'senha': senha,
        'padrao': padrao,
        'data_atual': datetime.date.today().strftime('%d.%m.%Y')
    }

    template = get_template('telefonia/pdf_senha.html')
    html_string = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

def gerar_pdf_senha(request, pk):
    pdf_bytes = get_pdf_senha_bytes(pk)
    if pdf_bytes:
        senha = CriarSenha.objects.get(pk=pk)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="senha_{senha.ramal}.pdf"'
        return response
    return HttpResponse("Erro ao gerar PDF", status=500)

from .models.padrao_tutorial import PadraoTutorialTelefonia

def get_pdf_tutorial_bytes():
    padrao = PadraoTutorialTelefonia.objects.filter(ativo=True).first()
    if not padrao:
        return None

    context = {
        'padrao': padrao,
    }
    
    template = get_template('telefonia/pdf_tutorial.html')
    html_string = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

def gerar_pdf_tutorial(request):
    pdf_bytes = get_pdf_tutorial_bytes()
    if pdf_bytes:
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="tutorial_telefonia.pdf"'
        return response
    return HttpResponse("Erro ao gerar PDF ou template não encontrado.", status=500)

class ContratoColaboradorViewSet(viewsets.ModelViewSet):
    queryset = ContratoColaborador.objects.all().order_by('-created_at')
    serializer_class = ContratoColaboradorSerializer
    pagination_class = None

