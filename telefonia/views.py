import datetime
from io import BytesIO

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.template.loader import get_template
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from xhtml2pdf import pisa

from .models import (
    TelefoneSolicitacao, AparelhoVoip, RemessaManutencao, CriarSenha, 
    AparelhoManutencao, ContratoColaborador, PadraoSenhaTelefonia, 
    PadraoTutorialTelefonia, PadraoEmailTelefonia
)
from .serializers import (
    TelefoneSolicitacaoSerializer,
    RemessaManutencaoSerializer, CriarSenhaSerializer, 
    ContratoColaboradorSerializer
)

from notificacoes.services import auto_message
from notificacoes.models.template_notificacao import TemplateMessage
from django.contrib.auth.models import User

# VIEWS TRADICIONAIS (TEMPLATES)
def main_telefonia(request):
    """Renderiza a tela principal de telefonia."""
    aparelhos_disponiveis = AparelhoVoip.objects.filter(status='estoque', integridade='funciona').count()
    aparelhos_instalados = AparelhoVoip.objects.filter(status='instalado').count()
    aparelhos_defeituosos = AparelhoVoip.objects.filter(status='defeituoso').count()
    aparelhos_manutencao = AparelhoVoip.objects.filter(status='manutencao').count()
    
    solicitacoes_pendentes = TelefoneSolicitacao.objects.exclude(status='concluida').count()
    solicitacoes_concluidas = TelefoneSolicitacao.objects.filter(status='concluida').count()
    
    remessas_total = RemessaManutencao.objects.count()
    total_senhas = CriarSenha.objects.count()
    
    tecnicos = User.objects.filter(groups__name__icontains='Telefonia')

    context = {
        'aparelhos_disponiveis': aparelhos_disponiveis,
        'aparelhos_instalados': aparelhos_instalados,
        'aparelhos_defeituosos': aparelhos_defeituosos,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'solicitacoes_concluidas': solicitacoes_concluidas,
        'remessas_total': remessas_total,
        'total_senhas': total_senhas,
        'tecnicos': tecnicos,
    }
    return render(request, 'telefonia/main_telefonia.html', context)


# DASHBOARD STATS
def dashboard_stats(request):
    """Retorna dados estatísticos para os gráficos da telefonia"""
    solicitacoes_status = TelefoneSolicitacao.objects.values('status').annotate(total=Count('id'))
    aparelhos_status = AparelhoVoip.objects.values('status').annotate(total=Count('id'))
    senhas_categoria = CriarSenha.objects.values('categoria').annotate(total=Count('id'))
    
    return JsonResponse({
        'solicitacoes': list(solicitacoes_status),
        'aparelhos': list(aparelhos_status),
        'senhas': list(senhas_categoria)
    })


# DRF VIEWSETS
class TelefoneSolicitacaoViewSet(viewsets.ModelViewSet):
    queryset = TelefoneSolicitacao.objects.all().order_by('-data')
    serializer_class = TelefoneSolicitacaoSerializer

    def perform_create(self, serializer):
        solicitacao = serializer.save()
        template = TemplateMessage.objects.filter(tipo_evento='tel_solicitacao_aparelho', is_ativo=True).first()
        if template:
            tecnicos = User.objects.filter(groups__name__icontains='Telefonia')
            for tecnico in tecnicos:
                if tecnico.perfil and tecnico.perfil.telefone:
                    tel = tecnico.perfil.telefone
                    texto = template.base_text
                    try:
                        text = texto.format(
                            tecnico=tecnico.get_full_name() or tecnico.username,
                            protocolo=solicitacao.protocolo or 'N/A',
                            unidade=solicitacao.unidade or 'N/A',
                            sigla_unidade=solicitacao.sigla_unidade or 'N/A',
                            ramal=solicitacao.ramal or 'N/A',
                            local=solicitacao.local or 'N/A',
                            qnt_solicitada=solicitacao.qnt_solicitada or 0,
                            solicitante=solicitacao.solicitante or 'N/A',
                        )
                        auto_message(tel, text)
                    except Exception as e:
                        print(f"Erro ao formatar/enviar mensagem: {e}")

    @action(detail=True, methods=['patch'])
    def concluir(self, request, pk=None):
        solicitacao = self.get_object()
        
        # Pega os outros campos
        solicitacao.tecnico_responsavel = request.data.get('tecnico_responsavel', solicitacao.tecnico_responsavel)
        solicitacao.relatorio = request.data.get('relatorio', solicitacao.relatorio)
        solicitacao.data_instalacao = request.data.get('data_instalacao', solicitacao.data_instalacao)
        solicitacao.termo_transferencia_interna = request.data.get('termo_transferencia_interna', solicitacao.termo_transferencia_interna)
        
        instalacoes = request.data.get('instalacoes', [])
        
        ramais_agrupados = []
        locais_agrupados = []
        aparelhos_salvar = []
        
        if instalacoes:
            from telefonia.models import AparelhoVoip
            for inst in instalacoes:
                ap_id = inst.get('aparelho_id')
                ramal = inst.get('ramal')
                local = inst.get('local')
                mac_address = inst.get('mac_address')
                
                if ap_id:
                    try:
                        ap = AparelhoVoip.objects.get(id=ap_id)
                        ap.status = 'instalado'
                        ap.ramal = ramal or ap.ramal
                        ap.sala = local or ap.sala
                        if mac_address:
                            ap.mac_address = mac_address
                        ap.save()
                        
                        aparelhos_salvar.append(ap)
                        
                        if ap.ramal:
                            ramais_agrupados.append(ap.ramal)
                        if ap.sala:
                            locais_agrupados.append(ap.sala)
                    except AparelhoVoip.DoesNotExist:
                        pass
                        
            solicitacao.aparelhos.set(aparelhos_salvar)
            
        solicitacao.status = 'concluida'
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aparelhos_ids = serializer.validated_data.pop('aparelhos', [])
        remessa = serializer.save()
        
        for ap_id in aparelhos_ids:
            try:
                ap_voip = AparelhoVoip.objects.get(id=ap_id)
                AparelhoManutencao.objects.create(
                    remessa=remessa,
                    patrimonio=ap_voip.patrimonio,
                    modelo=ap_voip.modelo,
                    fcn=ap_voip.fcn,
                    mac_address=ap_voip.mac_address,
                    ramal=ap_voip.ramal,
                    sala=ap_voip.sala,
                    integridade=ap_voip.integridade,
                    status='manutencao'
                )
                ap_voip.delete()
            except AparelhoVoip.DoesNotExist:
                continue
                
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CriarSenhaViewSet(viewsets.ModelViewSet):
    queryset = CriarSenha.objects.all().order_by('-created_at')
    serializer_class = CriarSenhaSerializer

    def perform_create(self, serializer):
        senha = serializer.save()
        template = TemplateMessage.objects.filter(tipo_evento='tel_solicitacao_senha', is_ativo=True).first()
        if template:
            tecnicos = User.objects.filter(groups__name__icontains='Telefonia')
            for tecnico in tecnicos:
                if tecnico.perfil and tecnico.perfil.telefone:
                    tel = tecnico.perfil.telefone
                    texto = template.base_text
                    try:
                        text = texto.format(
                            tecnico=tecnico.get_full_name() or tecnico.username,
                            protocolo=senha.protocolo or 'N/A',
                            unidade=senha.unidade or 'N/A',
                            sigla_unidade=senha.sigla_unidade or 'N/A',
                            ramal=senha.ramal or 'N/A',
                            usuario=senha.usuario or 'N/A',
                            solicitante=senha.solicitante or 'N/A',
                        )
                        auto_message(tel, text)
                    except Exception as e:
                        print(f"Erro ao formatar/enviar mensagem: {e}")


class ContratoColaboradorViewSet(viewsets.ModelViewSet):
    queryset = ContratoColaborador.objects.all().order_by('-created_at')
    serializer_class = ContratoColaboradorSerializer
    pagination_class = None


# PDF GENERATION
def gerar_pdf_remessa(request, pk):
    try:
        remessa = RemessaManutencao.objects.get(pk=pk)
    except RemessaManutencao.DoesNotExist:
        return HttpResponse("Remessa não encontrada", status=404)
        
    context = {'remessa': remessa}
    template = get_template('telefonia/pdf_remessa.html')
    html_string = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="remessa_{remessa.id}.pdf"'
        return response
    return HttpResponse("Erro ao gerar PDF", status=500)


def get_pdf_senha_bytes(senha_id=None, template_id=None):
    senha = CriarSenha.objects.get(pk=senha_id) if senha_id else None
    padrao = PadraoSenhaTelefonia.objects.get(pk=template_id) if template_id else PadraoSenhaTelefonia.objects.filter(ativo=True).first()
    
    if not padrao:
        return None
        
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
    pdf_bytes = get_pdf_senha_bytes(senha_id=pk)
    if pdf_bytes:
        senha = CriarSenha.objects.get(pk=pk)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        nome_usuario = senha.usuario if senha.usuario and senha.usuario != "N/A" else "Usuario"
        response['Content-Disposition'] = f'inline; filename="{nome_usuario}.pdf"'
        return response
    return HttpResponse("Erro ao gerar PDF", status=500)


def preview_pdf_senha_template(request, template_id):
    pdf_bytes = get_pdf_senha_bytes(template_id=template_id)
    if pdf_bytes:
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="preview_senha.pdf"'
        return response
    return HttpResponse("Erro ao gerar preview", status=500)


def get_pdf_tutorial_bytes(template_id=None):
    padrao = PadraoTutorialTelefonia.objects.get(pk=template_id) if template_id else PadraoTutorialTelefonia.objects.filter(ativo=True).first()
    if not padrao:
        return None

    context = {'padrao': padrao}
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
        response['Content-Disposition'] = 'inline; filename="Tutorial - Validação de Ligações A Serviço e Particulares.pdf"'
        return response
    return HttpResponse("Erro ao gerar PDF", status=500)


def preview_pdf_tutorial_template(request, template_id):
    pdf_bytes = get_pdf_tutorial_bytes(template_id=template_id)
    if pdf_bytes:
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="preview_tutorial.pdf"'
        return response
    return HttpResponse("Erro ao gerar preview", status=500)


def enviar_email_senha_manual(request, pk):
    from django.core.mail import EmailMessage
    from django.conf import settings
    try:
        senha_obj = CriarSenha.objects.get(pk=pk)
    except CriarSenha.DoesNotExist:
        return JsonResponse({"error": "Senha não encontrada."}, status=404)
        
    if not senha_obj.email:
        return JsonResponse({"error": "O usuário não possui um e-mail cadastrado."}, status=400)
        
    padrao_email = PadraoEmailTelefonia.objects.filter(ativo=True).first()
    if not padrao_email:
        return JsonResponse({"error": "Nenhum template de e-mail ativo foi encontrado."}, status=400)
        
    pdf_senha_bytes = get_pdf_senha_bytes(senha_id=pk)
    pdf_tutorial_bytes = get_pdf_tutorial_bytes()
    
    if not pdf_senha_bytes or not pdf_tutorial_bytes:
        return JsonResponse({"error": "Erro ao gerar os documentos em PDF para anexo."}, status=500)
        
    try:
        corpo_formatado = padrao_email.corpo.format(
            primeiro_nome=senha_obj.primeiro_nome or 'Usuário',
            senha=senha_obj.senha or 'Não registrada'
        )
    except Exception:
        corpo_formatado = padrao_email.corpo
        
    corpo = f"{corpo_formatado}\n\n{padrao_email.assinatura}" if padrao_email.assinatura else corpo_formatado
        
    assunto = padrao_email.assunto
    to_email = [senha_obj.email]
    bcc_email = [padrao_email.email_copia] if padrao_email.email_copia else []
    
    email = EmailMessage(
        subject=assunto,
        body=corpo,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_email,
        bcc=bcc_email
    )
    
    nome_usuario = senha_obj.usuario if senha_obj.usuario and senha_obj.usuario != "N/A" else "Usuario"
    email.attach(f'{nome_usuario}.pdf', pdf_senha_bytes, 'application/pdf')
    email.attach('Tutorial - Validação de Ligações A Serviço e Particulares.pdf', pdf_tutorial_bytes, 'application/pdf')
    
    try:
        email.send(fail_silently=False)
        return JsonResponse({"message": "E-mail enviado com sucesso!"})
    except Exception as e:
        return JsonResponse({"error": f"Erro ao enviar o e-mail: {str(e)}"}, status=500)
