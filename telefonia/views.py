import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from io import BytesIO

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Count, Q
from django.template.loader import get_template
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from xhtml2pdf import pisa

from .models import (
    TelefoneSolicitacao, AparelhoVoip, RemessaManutencao, CriarSenha, 
    AparelhoManutencao, ContratoColaborador, PadraoSenhaTelefonia, 
    PadraoTutorialTelefonia, PadraoEmailTelefonia, EmprestimoEvento,
    TelefoneSolicitacaoAnexo
)
from .serializers import (
    TelefoneSolicitacaoSerializer,
    RemessaManutencaoSerializer, CriarSenhaSerializer, 
    ContratoColaboradorSerializer, EmprestimoEventoSerializer
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
    
    eventos_ativos = EmprestimoEvento.objects.filter(status='em_andamento').count()
    
    remessas_total = RemessaManutencao.objects.count()
    total_senhas = CriarSenha.objects.count()
    
    tecnicos = User.objects.filter(groups__name__icontains='Telefonia')

    context = {
        'aparelhos_disponiveis': aparelhos_disponiveis,
        'aparelhos_instalados': aparelhos_instalados,
        'aparelhos_defeituosos': aparelhos_defeituosos,
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'solicitacoes_concluidas': solicitacoes_concluidas,
        'eventos_ativos': eventos_ativos,
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
            from notificacoes.models.contato_notificacao import Contato
            from notificacoes.services import disparar_notificacao_contato
            
            contatos = Contato.objects.filter(is_ativo=True, notifica_telefonia=True)
            enviados = set()
            for contato in contatos:
                # Verificação de duplicidade por telefone ou e-mail
                chave_duplicidade = getattr(contato, '_telefone_sanitizado', contato.telefone) or (contato.pessoa.email if contato.pessoa else None)
                if chave_duplicidade:
                    if chave_duplicidade in enviados:
                        continue
                    enviados.add(chave_duplicidade)
                
                texto = template.base_text
                try:
                    text = texto.format(
                        tecnico=contato.nome,
                        protocolo=solicitacao.protocolo or 'N/A',
                        unidade=solicitacao.unidade or 'N/A',
                        sigla_unidade=solicitacao.sigla_unidade or 'N/A',
                        ramal=solicitacao.ramal or 'N/A',
                        local=solicitacao.local or 'N/A',
                        qnt_solicitada=solicitacao.qnt_solicitada or 0,
                        solicitante=solicitacao.solicitante or 'N/A',
                    )
                    assunto = f"Nova Solicitação de Aparelho - {solicitacao.protocolo or 'N/A'}"
                    disparar_notificacao_contato(contato, text, text, assunto)
                except Exception as e:
                    print(f"Erro ao formatar/enviar mensagem: {e}")

    def perform_update(self, serializer):
        solicitacao = serializer.save()
        
        has_new_files = False
        import re
        for key, file in self.request.FILES.items():
            match = re.match(r'^pdf_termos_edit_(\d+)$', key)
            if match:
                has_new_files = True
                index = int(match.group(1))
                
                anexo, created = TelefoneSolicitacaoAnexo.objects.get_or_create(
                    solicitacao=solicitacao,
                    ordem=index
                )
                
                if not created and anexo.arquivo:
                    anexo.arquivo.delete(save=False)
                    
                safe_termo = ''.join(c for c in (solicitacao.termo_transferencia_interna or 'termo') if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                file.name = f"{safe_termo}_{solicitacao.protocolo}_{index}.pdf"
                anexo.arquivo = file
                anexo.save()
                
        if has_new_files:
            if hasattr(solicitacao, 'midia') and solicitacao.midia:
                solicitacao.midia.delete(save=False)
                solicitacao.midia = None
            if hasattr(solicitacao, 'pdf_termo') and solicitacao.pdf_termo:
                solicitacao.pdf_termo.delete(save=False)
                solicitacao.pdf_termo = None
            solicitacao.save()

    @action(detail=True, methods=['patch'])
    def concluir(self, request, pk=None):
        solicitacao = self.get_object()
        
        # Pega os outros campos
        solicitacao.tecnico_responsavel = request.data.get('tecnico_responsavel', solicitacao.tecnico_responsavel)
        solicitacao.relatorio = request.data.get('relatorio', solicitacao.relatorio)
        
        if 'data_instalacao' in request.data:
            data_inst_str = request.data.get('data_instalacao')
            if data_inst_str:
                dt = parse_datetime(data_inst_str)
                if dt:
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt)
                    solicitacao.data_instalacao = dt
            else:
                solicitacao.data_instalacao = None
                
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
            
        solicitacao.status = 'aguardando_supervisor_aparelho'
        if ramais_agrupados:
            solicitacao.ramal = ", ".join(ramais_agrupados)
        if locais_agrupados:
            solicitacao.local = ", ".join(locais_agrupados)
            
        solicitacao.save()
        return Response({'status': 'Solicitação técnica concluída com sucesso. Aguardando fase administrativa.'}, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def finalizar_administrativo(self, request, pk=None):
        solicitacao = self.get_object()
        
        if solicitacao.status != 'aguardando_supervisor_aparelho':
            return Response({'error': 'A solicitação não está na fase administrativa.'}, status=status.HTTP_400_BAD_REQUEST)
        termo = request.data.get('termo_transferencia_interna')
        pdf_termos = request.FILES.getlist('pdf_termos')
        
        if not termo or str(termo).strip() == '':
            return Response({'error': 'O preenchimento do número do Termo de Transferência Interna é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
        
        solicitacao.termo_transferencia_interna = termo
        solicitacao.status = 'concluida'
        solicitacao.save()
        
        import os
        import re
        safe_termo = re.sub(r'[^a-zA-Z0-9_-]', '', str(termo).replace('/', '').replace('\\', '').replace(' ', ''))
        
        # Limpar anexos antigos caso seja uma resubmissão para evitar duplicidade
        solicitacao.anexos.all().delete()
        
        for index, arquivo in enumerate(pdf_termos):
            ext = os.path.splitext(arquivo.name)[1]
            arquivo.name = f"TTI_{safe_termo}_{index+1}{ext}"
            TelefoneSolicitacaoAnexo.objects.create(
                solicitacao=solicitacao,
                arquivo=arquivo,
                ordem=index
            )
            
        # Manter compatibilidade com o serializer salvando apenas que a ação foi registrada no log.
        return Response({'status': 'Solicitação administrativa concluída com sucesso.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='excluir_anexo/(?P<anexo_id>[^/.]+)')
    def excluir_anexo(self, request, pk=None, anexo_id=None):
        solicitacao = self.get_object()
        
        if anexo_id == 'legacy':
            if solicitacao.pdf_termo:
                solicitacao.pdf_termo.delete(save=False)
                solicitacao.pdf_termo = None
            if solicitacao.midia:
                solicitacao.midia.delete(save=False)
                solicitacao.midia = None
            solicitacao.save()
            return Response({'status': 'Anexo legado excluído com sucesso.'}, status=status.HTTP_200_OK)
            
        try:
            anexo = TelefoneSolicitacaoAnexo.objects.get(id=anexo_id, solicitacao=solicitacao)
            anexo.arquivo.delete(save=False)
            anexo.delete()
            return Response({'status': 'Anexo excluído com sucesso.'}, status=status.HTTP_200_OK)
        except TelefoneSolicitacaoAnexo.DoesNotExist:
            return Response({'error': 'Anexo não encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class EmprestimoEventoViewSet(viewsets.ModelViewSet):
    queryset = EmprestimoEvento.objects.all().order_by('-created_at')
    serializer_class = EmprestimoEventoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aparelhos_instances = serializer.validated_data.pop('aparelhos', [])
        
        # Validar data_inicio e data_fim
        if 'data_inicio' in request.data:
            dt = parse_datetime(request.data['data_inicio'])
            if dt and timezone.is_naive(dt): dt = timezone.make_aware(dt)
            serializer.validated_data['data_inicio'] = dt
        
        if 'data_fim' in request.data:
            dt = parse_datetime(request.data['data_fim'])
            if dt and timezone.is_naive(dt): dt = timezone.make_aware(dt)
            serializer.validated_data['data_fim'] = dt

        evento = serializer.save()

        # Adicionar os aparelhos e marcar como 'instalado'
        if aparelhos_instances:
            for ap in aparelhos_instances:
                ap.status = 'instalado'
                ap.save()
            evento.aparelhos.set(aparelhos_instances)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def recolher(self, request, pk=None):
        evento = self.get_object()
        
        if evento.status == 'concluido':
            return Response({'error': 'Evento já foi concluído.'}, status=status.HTTP_400_BAD_REQUEST)

        evento.observacoes = request.data.get('observacoes', evento.observacoes)
        evento.status = 'concluido'
        evento.save()

        # Devolver aparelhos ao estoque
        for ap in evento.aparelhos.all():
            ap.status = 'estoque'
            ap.save()

        return Response({'status': 'Equipamentos recolhidos e evento concluído com sucesso.'}, status=status.HTTP_200_OK)



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

    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        data = request.data
        colaboradores = data.get('colaboradores')

        if colaboradores and isinstance(colaboradores, list):
            senhas_criadas = []
            for colab in colaboradores:
                # Usa dict() para garantir compatibilidade com QueryDict e JSON
                colab_data = dict(data)
                colab_data.pop('colaboradores', None)  # Remove a lista para nao atrapalhar o serializer
                colab_data.update(colab)
                serializer = self.get_serializer(data=colab_data)
                if not serializer.is_valid():
                    logger.error(f"[CriarSenha.create] Erros de validação: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                self.perform_create(serializer)
                senhas_criadas.append(serializer.data)
            return Response(senhas_criadas, status=status.HTTP_201_CREATED)
        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        senha = serializer.save(status='recebida')

        # Se cargo for colaborador e houver numero_contrato, salva/atualiza o contrato na tabela
        if senha.cargo == 'colaborador' and senha.numero_contrato:
            try:
                contrato, criado = ContratoColaborador.objects.get_or_create(
                    numero_contrato=senha.numero_contrato,
                    defaults={
                        'empresa_vinculada': senha.empresa_vinculada or '',
                        'fiscal_contrato': senha.fiscal_contrato or '',
                        'unidade_fiscal': senha.unidade_fiscal or '',
                    }
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"[perform_create] Erro ao salvar ContratoColaborador: {e}")

        template = TemplateMessage.objects.filter(tipo_evento='tel_solicitacao_senha', is_ativo=True).first()
        if template:
            from notificacoes.models.contato_notificacao import Contato
            from notificacoes.services import disparar_notificacao_contato
            
            contatos = Contato.objects.filter(is_ativo=True, notifica_telefonia=True)
            enviados = set()
            for contato in contatos:
                # Verificação de duplicidade por telefone ou e-mail
                chave_duplicidade = getattr(contato, '_telefone_sanitizado', contato.telefone) or (contato.pessoa.email if contato.pessoa else None)
                if chave_duplicidade:
                    if chave_duplicidade in enviados:
                        continue
                    enviados.add(chave_duplicidade)
                
                texto = template.base_text
                try:
                    text = texto.format(
                        tecnico=contato.nome,
                        protocolo=senha.protocolo or 'N/A',
                        unidade=senha.unidade or 'N/A',
                        sigla_unidade=senha.sigla_unidade or 'N/A',
                        ramal=senha.ramal or 'N/A',
                        usuario=senha.usuario or 'N/A',
                        solicitante=senha.solicitante or 'N/A',
                    )
                    assunto = f"Nova Solicitação de Senha - {senha.protocolo or 'N/A'}"
                    disparar_notificacao_contato(contato, text, text, assunto)
                except Exception as e:
                    print(f"Erro ao formatar/enviar mensagem: {e}")

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'aguardando_supervisor' and not instance.nome_tecnico:
            instance.nome_tecnico = self.request.user.get_full_name() or self.request.user.username
            instance.save(update_fields=['nome_tecnico'])

    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        senha_obj = self.get_object()
        data = request.data
        
        # Atualiza dados
        senha_obj.cargo = data.get('cargo', senha_obj.cargo)
        senha_obj.numero_contrato = data.get('numero_contrato', senha_obj.numero_contrato)
        senha_obj.empresa_vinculada = data.get('empresa_vinculada', senha_obj.empresa_vinculada)
        senha_obj.fiscal_contrato = data.get('fiscal_contrato', senha_obj.fiscal_contrato)
        senha_obj.unidade_fiscal = data.get('unidade_fiscal', senha_obj.unidade_fiscal)
        senha_obj.status = 'finalizada'
        senha_obj.save()
        
        # Envio de e-mail customizado pelo supervisor
        assunto = data.get('assunto')
        corpo = data.get('corpo')
        to_email = data.get('to_email')
        bcc_email = data.get('bcc_email')
        
        from telefonia.views import enviar_email_senha_manual
        # Mock request to pass data to the old function or just update the function
        request._request.POST = request._request.POST.copy()
        if assunto: request._request.POST['assunto'] = assunto
        if corpo: request._request.POST['corpo'] = corpo
        if to_email: request._request.POST['to_email'] = to_email
        if bcc_email: request._request.POST['bcc_email'] = bcc_email
        
        try:
            resp = enviar_email_senha_manual(request._request, pk=senha_obj.pk)
            import json
            resp_content = json.loads(resp.content)
            if resp.status_code == 200:
                return Response({'status': 'Senha finalizada e e-mail enviado.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': resp_content.get('error', 'Erro ao enviar email.')}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Erro ao finalizar: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='email-preview')
    def email_preview(self, request, pk=None):
        senha_obj = self.get_object()
        from telefonia.models.padrao_email import PadraoEmailTelefonia
        padrao = PadraoEmailTelefonia.objects.filter(ativo=True).first()
        if not padrao:
            return Response({"error": "Nenhum template de e-mail ativo."}, status=400)
            
        try:
            corpo_formatado = padrao.corpo.format(
                primeiro_nome=senha_obj.primeiro_nome or 'Usuário',
                senha=senha_obj.senha or 'Não registrada'
            )
        except:
            corpo_formatado = padrao.corpo
            
        corpo = f"{corpo_formatado}\n\n{padrao.assinatura}" if padrao.assinatura else corpo_formatado
        
        from django.utils.text import slugify
        nome_usuario = slugify(senha_obj.usuario) if senha_obj.usuario and senha_obj.usuario != "N/A" else "documento_senha"
        
        return Response({
            'to_email': senha_obj.email or '',
            'bcc_email': padrao.email_copia or '',
            'assunto': padrao.assunto or '',
            'corpo': corpo,
            'filename': f"{nome_usuario}.pdf"
        })

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
        from django.utils.text import slugify
        nome_usuario = slugify(senha.usuario) if senha.usuario and senha.usuario != "N/A" else "usuario"
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
        
    corpo_default = f"{corpo_formatado}\n\n{padrao_email.assinatura}" if padrao_email.assinatura else corpo_formatado
        
    assunto = request.POST.get('assunto') or padrao_email.assunto
    corpo = request.POST.get('corpo') or corpo_default
    
    to_email_val = request.POST.get('to_email') or senha_obj.email
    to_email = [to_email_val] if to_email_val else []
    
    bcc_email_val = request.POST.get('bcc_email') or padrao_email.email_copia
    bcc_email = [bcc_email_val] if bcc_email_val else []
    
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
i m p o r t   i o  
 i m p o r t   b a s e 6 4  
 i m p o r t   m a t p l o t l i b  
 m a t p l o t l i b . u s e ( ' A g g ' )  
 i m p o r t   m a t p l o t l i b . p y p l o t   a s   p l t  
 i m p o r t   o p e n p y x l  
 f r o m   o p e n p y x l . c h a r t   i m p o r t   P i e C h a r t ,   R e f e r e n c e  
 f r o m   o p e n p y x l . s t y l e s   i m p o r t   F o n t ,   A l i g n m e n t ,   P a t t e r n F i l l  
 f r o m   o p e n p y x l . u t i l s   i m p o r t   g e t _ c o l u m n _ l e t t e r  
  
 f r o m   d j a n g o . h t t p   i m p o r t   H t t p R e s p o n s e  
 f r o m   d j a n g o . t e m p l a t e . l o a d e r   i m p o r t   g e t _ t e m p l a t e  
 f r o m   d j a n g o . v i e w s   i m p o r t   V i e w  
 f r o m   d j a n g o . u t i l s   i m p o r t   t i m e z o n e  
 f r o m   x h t m l 2 p d f   i m p o r t   p i s a  
  
 f r o m   t e l e f o n i a . m o d e l s   i m p o r t   A p a r e l h o V o i p  
  
 c l a s s   A p a r e l h o s R e p o r t V i e w ( V i e w ) :  
         d e f   g e t ( s e l f ,   r e q u e s t ,   * a r g s ,   * * k w a r g s ) :  
                 f o r m a t o   =   r e q u e s t . G E T . g e t ( ' f o r m a t o ' ,   ' p d f ' ) . l o w e r ( )  
                  
                 #   P e g a   t o d o s   o s   a p a r e l h o s  
                 a p a r e l h o s   =   A p a r e l h o V o i p . o b j e c t s . a l l ( )  
                  
                 #   E s t a t � � s t i c a s   p a r a   o   g r � � f i c o  
                 c o u n t s   =   {  
                         ' e s t o q u e ' :   a p a r e l h o s . f i l t e r ( s t a t u s = ' e s t o q u e ' ) . c o u n t ( ) ,  
                         ' i n s t a l a d o ' :   a p a r e l h o s . f i l t e r ( s t a t u s = ' i n s t a l a d o ' ) . c o u n t ( ) ,  
                         ' m a n u t e n c a o ' :   a p a r e l h o s . f i l t e r ( s t a t u s = ' m a n u t e n c a o ' ) . c o u n t ( ) ,  
                         ' d e f e i t u o s o ' :   a p a r e l h o s . f i l t e r ( s t a t u s = ' d e f e i t u o s o ' ) . c o u n t ( ) ,  
                 }  
                  
                 #   F i l t r a   a   l i s t a   p r i n c i p a l   p a r a   e x i b i r   a p e n a s   o s   i n s t a l a d o s  
                 a p a r e l h o s _ l i s t a   =   a p a r e l h o s . f i l t e r ( s t a t u s = ' i n s t a l a d o ' ) . o r d e r _ b y ( ' s a l a ' ,   ' p a t r i m o n i o ' )  
                  
                 i f   f o r m a t o   = =   ' e x c e l ' :  
                         r e t u r n   s e l f . e x p o r t _ e x c e l ( c o u n t s ,   a p a r e l h o s _ l i s t a )  
                 e l s e :  
                         r e t u r n   s e l f . e x p o r t _ p d f ( c o u n t s ,   a p a r e l h o s _ l i s t a )  
  
         d e f   g e n e r a t e _ c h a r t _ b a s e 6 4 ( s e l f ,   c o u n t s ) :  
                 l a b e l s   =   [ ' E m   E s t o q u e ' ,   ' I n s t a l a d o s ' ,   ' E m   M a n u t e n � � � � o ' ,   ' D e f e i t u o s o s ' ]  
                 s i z e s   =   [ c o u n t s [ ' e s t o q u e ' ] ,   c o u n t s [ ' i n s t a l a d o ' ] ,   c o u n t s [ ' m a n u t e n c a o ' ] ,   c o u n t s [ ' d e f e i t u o s o ' ] ]  
                 c o l o r s   =   [ ' # 0 0 7 b f f ' ,   ' # 2 8 a 7 4 5 ' ,   ' # f f c 1 0 7 ' ,   ' # d c 3 5 4 5 ' ]  
                  
                 #   R e m o v e   z e r o s   t o   p r e v e n t   e m p t y   s l i c e s  
                 f i l t e r e d _ l a b e l s   =   [ l   f o r   l ,   s   i n   z i p ( l a b e l s ,   s i z e s )   i f   s   >   0 ]  
                 f i l t e r e d _ s i z e s   =   [ s   f o r   s   i n   s i z e s   i f   s   >   0 ]  
                 f i l t e r e d _ c o l o r s   =   [ c   f o r   c ,   s   i n   z i p ( c o l o r s ,   s i z e s )   i f   s   >   0 ]  
                  
                 f i g ,   a x   =   p l t . s u b p l o t s ( f i g s i z e = ( 6 ,   4 ) )  
                 i f   f i l t e r e d _ s i z e s :  
                         a x . p i e ( f i l t e r e d _ s i z e s ,   l a b e l s = f i l t e r e d _ l a b e l s ,   c o l o r s = f i l t e r e d _ c o l o r s ,   a u t o p c t = ' % 1 . 1 f % % ' ,   s t a r t a n g l e = 1 4 0 )  
                         a x . a x i s ( ' e q u a l ' )  
                 e l s e :  
                         a x . t e x t ( 0 . 5 ,   0 . 5 ,   ' N e n h u m   d a d o   d i s p o n � � v e l ' ,   h o r i z o n t a l a l i g n m e n t = ' c e n t e r ' ,   v e r t i c a l a l i g n m e n t = ' c e n t e r ' )  
                  
                 p l t . t i t l e ( ' D e s e m p e n h o   d a   G e s t � � o   d e   A p a r e l h o s ' )  
                  
                 b u f f e r   =   i o . B y t e s I O ( )  
                 p l t . s a v e f i g ( b u f f e r ,   f o r m a t = ' p n g ' ,   t r a n s p a r e n t = T r u e ,   b b o x _ i n c h e s = ' t i g h t ' )  
                 p l t . c l o s e ( f i g )  
                 b u f f e r . s e e k ( 0 )  
                  
                 i m g _ s t r   =   b a s e 6 4 . b 6 4 e n c o d e ( b u f f e r . r e a d ( ) ) . d e c o d e ( ' u t f - 8 ' )  
                 r e t u r n   f " d a t a : i m a g e / p n g ; b a s e 6 4 , { i m g _ s t r } "  
  
         d e f   e x p o r t _ p d f ( s e l f ,   c o u n t s ,   a p a r e l h o s _ l i s t a ) :  
                 t e m p l a t e   =   g e t _ t e m p l a t e ( ' t e l e f o n i a / r e l a t o r i o s / r e l a t o r i o _ a p a r e l h o s _ p d f . h t m l ' )  
                 c h a r t _ u r i   =   s e l f . g e n e r a t e _ c h a r t _ b a s e 6 4 ( c o u n t s )  
                  
                 c o n t e x t   =   {  
                         ' c o u n t s ' :   c o u n t s ,  
                         ' a p a r e l h o s ' :   a p a r e l h o s _ l i s t a ,  
                         ' c h a r t _ u r i ' :   c h a r t _ u r i ,  
                         ' d a t a _ e m i s s a o ' :   t i m e z o n e . n o w ( )  
                 }  
                  
                 h t m l   =   t e m p l a t e . r e n d e r ( c o n t e x t )  
                 r e s p o n s e   =   H t t p R e s p o n s e ( c o n t e n t _ t y p e = ' a p p l i c a t i o n / p d f ' )  
                 r e s p o n s e [ ' C o n t e n t - D i s p o s i t i o n ' ]   =   f ' i n l i n e ;   f i l e n a m e = " r e l a t o r i o _ a p a r e l h o s _ { t i m e z o n e . n o w ( ) . s t r f t i m e ( " % Y % m % d _ % H % M % S " ) } . p d f " '  
                  
                 p i s a _ s t a t u s   =   p i s a . C r e a t e P D F (  
                         h t m l ,   d e s t = r e s p o n s e  
                 )  
                 i f   p i s a _ s t a t u s . e r r :  
                         r e t u r n   H t t p R e s p o n s e ( ' T i v e m o s   a l g u n s   e r r o s   < p r e > '   +   h t m l   +   ' < / p r e > ' )  
                 r e t u r n   r e s p o n s e  
  
         d e f   e x p o r t _ e x c e l ( s e l f ,   c o u n t s ,   a p a r e l h o s _ l i s t a ) :  
                 w b   =   o p e n p y x l . W o r k b o o k ( )  
                 w s   =   w b . a c t i v e  
                 w s . t i t l e   =   " A p a r e l h o s   I n s t a l a d o s "  
                  
                 #   H e a d e r   d a   t a b e l a  
                 h e a d e r s   =   [ ' P a t r i m � � n i o ' ,   ' M o d e l o ' ,   ' M A C   A d d r e s s ' ,   ' R a m a l ' ,   ' I n t e g r i d a d e ' ,   ' L o c a l / S a l a ' ]  
                 f o r   c o l _ n u m ,   h e a d e r   i n   e n u m e r a t e ( h e a d e r s ,   1 ) :  
                         c e l l   =   w s . c e l l ( r o w = 1 ,   c o l u m n = c o l _ n u m ,   v a l u e = h e a d e r )  
                         c e l l . f o n t   =   F o n t ( b o l d = T r u e ,   c o l o r = " F F F F F F " )  
                         c e l l . f i l l   =   P a t t e r n F i l l ( s t a r t _ c o l o r = " 4 F 8 1 B D " ,   e n d _ c o l o r = " 4 F 8 1 B D " ,   f i l l _ t y p e = " s o l i d " )  
                         c e l l . a l i g n m e n t   =   A l i g n m e n t ( h o r i z o n t a l = " c e n t e r " )  
                         w s . c o l u m n _ d i m e n s i o n s [ g e t _ c o l u m n _ l e t t e r ( c o l _ n u m ) ] . w i d t h   =   2 0  
                  
                 #   P o p u l a   a   t a b e l a  
                 r o w _ n u m   =   2  
                 f o r   a p a r e l h o   i n   a p a r e l h o s _ l i s t a :  
                         w s . c e l l ( r o w = r o w _ n u m ,   c o l u m n = 1 ,   v a l u e = a p a r e l h o . p a t r i m o n i o   o r   ' - ' )  
                         w s . c e l l ( r o w = r o w _ n u m ,   c o l u m n = 2 ,   v a l u e = a p a r e l h o . m o d e l o   o r   ' - ' )  
                         w s . c e l l ( r o w = r o w _ n u m ,   c o l u m n = 3 ,   v a l u e = a p a r e l h o . m a c _ a d d r e s s   o r   ' - ' )  
                         w s . c e l l ( r o w = r o w _ n u m ,   c o l u m n = 4 ,   v a l u e = a p a r e l h o . r a m a l   o r   ' - ' )  
                         w s . c e l l ( r o w = r o w _ n u m ,   c o l u m n = 5 ,   v a l u e = a p a r e l h o . g e t _ i n t e g r i d a d e _ d i s p l a y ( )   i f   a p a r e l h o . i n t e g r i d a d e   e l s e   ' - ' )  
                         w s . c e l l ( r o w = r o w _ n u m ,   c o l u m n = 6 ,   v a l u e = a p a r e l h o . s a l a   o r   ' - ' )  
                         r o w _ n u m   + =   1  
                          
                 #   A b a   d e   G r � � f i c o  
                 w s _ c h a r t   =   w b . c r e a t e _ s h e e t ( t i t l e = " D e s e m p e n h o   ( G r � � f i c o ) " )  
                 w s _ c h a r t . c e l l ( r o w = 1 ,   c o l u m n = 1 ,   v a l u e = " S t a t u s " )  
                 w s _ c h a r t . c e l l ( r o w = 1 ,   c o l u m n = 2 ,   v a l u e = " Q u a n t i d a d e " )  
                  
                 s t a t u s _ d a t a   =   [  
                         ( " E m   E s t o q u e " ,   c o u n t s [ ' e s t o q u e ' ] ) ,  
                         ( " I n s t a l a d o s " ,   c o u n t s [ ' i n s t a l a d o ' ] ) ,  
                         ( " E m   M a n u t e n � � � � o " ,   c o u n t s [ ' m a n u t e n c a o ' ] ) ,  
                         ( " D e f e i t u o s o s " ,   c o u n t s [ ' d e f e i t u o s o ' ] ) ,  
                 ]  
                  
                 f o r   i d x ,   ( l a b e l ,   c o u n t )   i n   e n u m e r a t e ( s t a t u s _ d a t a ,   2 ) :  
                         w s _ c h a r t . c e l l ( r o w = i d x ,   c o l u m n = 1 ,   v a l u e = l a b e l )  
                         w s _ c h a r t . c e l l ( r o w = i d x ,   c o l u m n = 2 ,   v a l u e = c o u n t )  
                          
                 p i e   =   P i e C h a r t ( )  
                 l a b e l s   =   R e f e r e n c e ( w s _ c h a r t ,   m i n _ c o l = 1 ,   m i n _ r o w = 2 ,   m a x _ r o w = 5 )  
                 d a t a   =   R e f e r e n c e ( w s _ c h a r t ,   m i n _ c o l = 2 ,   m i n _ r o w = 1 ,   m a x _ r o w = 5 )  
                 p i e . a d d _ d a t a ( d a t a ,   t i t l e s _ f r o m _ d a t a = T r u e )  
                 p i e . s e t _ c a t e g o r i e s ( l a b e l s )  
                 p i e . t i t l e   =   " D e s e m p e n h o   d a   G e s t � � o   d e   A p a r e l h o s "  
                  
                 w s _ c h a r t . a d d _ c h a r t ( p i e ,   " D 2 " )  
  
                 r e s p o n s e   =   H t t p R e s p o n s e ( c o n t e n t _ t y p e = ' a p p l i c a t i o n / v n d . o p e n x m l f o r m a t s - o f f i c e d o c u m e n t . s p r e a d s h e e t m l . s h e e t ' )  
                 r e s p o n s e [ ' C o n t e n t - D i s p o s i t i o n ' ]   =   f ' a t t a c h m e n t ;   f i l e n a m e = r e l a t o r i o _ a p a r e l h o s _ { t i m e z o n e . n o w ( ) . s t r f t i m e ( " % Y % m % d _ % H % M % S " ) } . x l s x '  
                 w b . s a v e ( r e s p o n s e )  
                  
                 r e t u r n   r e s p o n s e  
 