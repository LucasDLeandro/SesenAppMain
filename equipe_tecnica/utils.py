from django.core.mail import EmailMessage
from django.conf import settings
from .models import LiberacaoAcessoDiaria, PadraoEmailLiberacao
import logging

logger = logging.getLogger(__name__)

FALLBACK_CORPO = (
    "Empresa: {empresa}\n"
    "Solicitante: {solicitante}\n"
    "Período: {periodo}\n"
    "Datas: {datas}\n"
    "Técnicos:\n{tecnicos}"
)


def get_template_liberacao_ativo():
    template = PadraoEmailLiberacao.objects.filter(ativo=True).first()
    if template:
        return template

    return PadraoEmailLiberacao(
        nome="Template Padrão (fallback)",
        assunto="Liberação de Acesso",
        corpo=FALLBACK_CORPO,
        assinatura="Equipe Técnica",
    )


def montar_email_liberacao(liberacao):
    template = get_template_liberacao_ativo()

    empresa = liberacao.solicitacao.empresa.nome_empresa
    solicitante = liberacao.solicitacao.nome_solicitante
    
    if liberacao.hora_inicio and liberacao.hora_fim:
        periodo = f"{liberacao.hora_inicio.strftime('%H:%M')} às {liberacao.hora_fim.strftime('%H:%M')}"
    else:
        periodo = "Horário não definido"

    if liberacao.data_inicio == liberacao.data_fim:
        datas = f"{liberacao.data_inicio.strftime('%d/%m/%Y')}"
    else:
        datas = (
            f"{liberacao.data_inicio.strftime('%d/%m/%Y')} a "
            f"{liberacao.data_fim.strftime('%d/%m/%Y')}"
        )

    tecnicos_str = "\n".join(
        [f"- {t.nome} (CPF: {t.cpf} | RG: {t.rg or 'N/A'})" for t in liberacao.tecnicos.all()]
    )

    corpo = template.corpo
    corpo = corpo.replace('{empresa}', empresa)
    corpo = corpo.replace('{solicitante}', solicitante)
    corpo = corpo.replace('{periodo}', periodo)
    corpo = corpo.replace('{datas}', datas)
    corpo = corpo.replace('{tecnicos}', tecnicos_str)

    mensagem_final = f"{corpo}\n\n{template.assinatura}"
    remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)

    destinatario = template.email_destinatario or ''
    copia_cc = template.email_copia or ''
    pode_enviar = bool(destinatario)

    erro = None
    if not destinatario:
        erro = (
            'O template ativo não possui e-mail destinatário configurado. '
            'Configure em Configurações → Liberação de Acesso.'
        )

    return {
        'assunto': template.assunto,
        'corpo': mensagem_final,
        'destinatario': destinatario,
        'copia_cc': copia_cc,
        'remetente': remetente,
        'template_nome': template.nome,
        'pode_enviar': pode_enviar,
        'erro': erro,
        'empresa': empresa,
        'solicitante': solicitante,
        'periodo': periodo,
        'datas': datas,
    }


def enviar_email_liberacao(liberacao_id, custom_to=None, custom_cc=None, custom_subject=None, custom_body=None, anexos=None):
    try:
        liberacao = LiberacaoAcessoDiaria.objects.get(id=liberacao_id)
        dados = montar_email_liberacao(liberacao)

        assunto = custom_subject if custom_subject is not None else dados['assunto']
        corpo = custom_body if custom_body is not None else dados['corpo']
        remetente = dados['remetente']
        destinatario = custom_to if custom_to is not None else dados['destinatario']
        copia_cc = custom_cc if custom_cc is not None else dados['copia_cc']

        if not destinatario:
            logger.error(
                "Nenhum destinatário configurado para a liberação %s.",
                liberacao_id,
            )
            return False

        cc_list = [c.strip() for c in copia_cc.split(',') if c.strip()] if copia_cc else None
        to_list = [d.strip() for d in destinatario.split(',') if d.strip()]

        email = EmailMessage(
            subject=assunto,
            body=corpo,
            from_email=remetente,
            to=to_list,
            cc=cc_list,
        )
        
        # Adiciona os anexos, se existirem
        if anexos:
            for anexo in anexos:
                email.attach(anexo.name, anexo.read(), anexo.content_type)

        email.send(fail_silently=False)

        liberacao.email_enviado = True
        liberacao.save(update_fields=['email_enviado'])
        return True

    except LiberacaoAcessoDiaria.DoesNotExist:
        logger.error("Liberação %s não encontrada.", liberacao_id)
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de liberação {liberacao_id}: {e}")
        return False
