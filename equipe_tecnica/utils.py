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
    periodo = liberacao.periodo

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
    copia_oculta = template.email_copia or ''
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
        'copia_oculta': copia_oculta,
        'remetente': remetente,
        'template_nome': template.nome,
        'pode_enviar': pode_enviar,
        'erro': erro,
        'empresa': empresa,
        'solicitante': solicitante,
        'periodo': periodo,
        'datas': datas,
    }


def enviar_email_liberacao(liberacao_id):
    try:
        liberacao = LiberacaoAcessoDiaria.objects.get(id=liberacao_id)
        dados = montar_email_liberacao(liberacao)

        if not dados['pode_enviar']:
            logger.error(
                "Template de liberação ativo sem e-mail destinatário configurado (liberação %s).",
                liberacao_id,
            )
            return False

        bcc_list = [dados['copia_oculta']] if dados['copia_oculta'] else None

        email = EmailMessage(
            subject=dados['assunto'],
            body=dados['corpo'],
            from_email=dados['remetente'],
            to=[dados['destinatario']],
            bcc=bcc_list,
        )
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
