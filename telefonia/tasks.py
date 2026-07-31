from django.utils import timezone
from datetime import timedelta
from telefonia.models import EmprestimoEvento
from notificacoes.models.contato_notificacao import Contato
from notificacoes.models.template_notificacao import TemplateMessage
from notificacoes.services import disparar_notificacao_contato
import logging

logger = logging.getLogger(__name__)

def verificar_e_notificar_eventos():
    logger.info("Iniciando verificação de eventos telefônicos pendentes de recolhimento.")
    agora = timezone.now()
    limite_notificacao = agora + timedelta(hours=24)

    eventos_pendentes = EmprestimoEvento.objects.filter(
        status='em_andamento',
        data_fim__lte=limite_notificacao,
        notificacao_enviada=False
    )

    if not eventos_pendentes.exists():
        logger.info("Nenhum evento pendente de recolhimento no momento.")
        return

    # Busca o template no banco
    template = TemplateMessage.objects.filter(tipo_evento='tel_recolhimento_evento', is_ativo=True).first()
    if not template:
        logger.warning("Template 'tel_recolhimento_evento' não encontrado ou inativo. Abortando notificações.")
        return
        
    contatos_to_notify = template.contatos.filter(is_ativo=True)
    
    # Fallback: Se o template não tem contatos selecionados, tenta pegar todos os que têm notifica_telefonia=True
    if not contatos_to_notify.exists():
        contatos_to_notify = Contato.objects.filter(is_ativo=True, notifica_telefonia=True)

    if not contatos_to_notify.exists():
        logger.warning("Nenhum contato cadastrado para receber notificações de eventos.")
        return

    for evento in eventos_pendentes:
        # Formata o texto do template com os dados do evento
        mensagem = template.base_text.format(
            evento_nome=evento.evento_nome,
            data_fim=evento.data_fim.strftime('%d/%m/%Y às %H:%M'),
            local=evento.local,
            solicitante=evento.solicitante
        )
        
        assunto = f"Recolhimento Pendente: {evento.evento_nome}"

        # Evita duplicidade enviando para cada contato uma única vez
        enviados = set()
        for contato in contatos_to_notify:
            chave = getattr(contato, '_telefone_sanitizado', contato.telefone) or (contato.pessoa.email if contato.pessoa else None)
            if chave:
                if chave in enviados:
                    continue
                enviados.add(chave)

            try:
                disparar_notificacao_contato(contato, mensagem, mensagem, assunto)
            except Exception as e:
                logger.error(f"Erro ao notificar {contato.nome}: {e}")
        
        logger.info(f"Notificações enviadas para o evento {evento.evento_nome}.")
        
        # Marca como enviada para não repetir
        evento.notificacao_enviada = True
        evento.save(update_fields=['notificacao_enviada'])
