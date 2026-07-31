from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from telefonia.models import EmprestimoEvento
from notificacoes.models.contato_notificacao import Contato
from notificacoes.services import disparar_notificacao_contato
from logs.models import SystemLog

class Command(BaseCommand):
    help = 'Notifica contatos de telefonia sobre equipamentos de eventos que precisam ser recolhidos hoje.'

    def handle(self, *args, **options):
        # Encontra eventos 'em_andamento' cuja data_fim seja menor ou igual a (agora + 24 horas)
        agora = timezone.now()
        limite_notificacao = agora + timedelta(hours=24)

        eventos_pendentes = EmprestimoEvento.objects.filter(
            status='em_andamento',
            data_fim__lte=limite_notificacao
        )

        if not eventos_pendentes.exists():
            self.stdout.write(self.style.SUCCESS("Nenhum evento pendente de recolhimento no momento."))
            return

        # Contatos configurados para receber alertas de telefonia
        contatos = Contato.objects.filter(is_ativo=True, notifica_telefonia=True)
        if not contatos.exists():
            self.stdout.write(self.style.WARNING("Nenhum contato de telefonia cadastrado para receber notificações."))
            return

        for evento in eventos_pendentes:
            mensagem = (
                f"⚠️ *LEMBRETE DE RECOLHIMENTO*\n\n"
                f"O evento *{evento.evento_nome}* tem recolhimento de aparelhos previsto para o prazo limite.\n"
                f"Data Fim: {evento.data_fim.strftime('%d/%m/%Y às %H:%M')}\n"
                f"Local: {evento.local}\n"
                f"Solicitante: {evento.solicitante}\n\n"
                f"Por favor, acesse a Dashboard de Telefonia no SesenApp para efetuar a baixa."
            )
            assunto = f"Recolhimento Pendente: {evento.evento_nome}"

            # Evita duplicidade enviando para cada contato
            enviados = set()
            for contato in contatos:
                chave = getattr(contato, '_telefone_sanitizado', contato.telefone) or (contato.pessoa.email if contato.pessoa else None)
                if chave:
                    if chave in enviados:
                        continue
                    enviados.add(chave)

                try:
                    disparar_notificacao_contato(contato, mensagem, mensagem, assunto)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erro ao notificar {contato.nome}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f"Notificações enviadas para o evento {evento.evento_nome}."))
