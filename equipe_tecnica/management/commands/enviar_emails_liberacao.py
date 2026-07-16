from django.core.management.base import BaseCommand
from django.utils import timezone
from equipe_tecnica.models import LiberacaoAcessoDiaria
from equipe_tecnica.utils import enviar_email_liberacao

class Command(BaseCommand):
    help = 'Envia e-mails agendados para a segurança referentes à liberação de acesso'

    def handle(self, *args, **kwargs):
        agora = timezone.now()
        
        # Pega todas as liberações com data programada para antes ou igual ao momento atual 
        # que ainda não foram enviadas
        liberacoes = LiberacaoAcessoDiaria.objects.filter(
            email_enviado=False,
            data_agendamento_email__isnull=False,
            data_agendamento_email__lte=agora
        )
        
        if not liberacoes.exists():
            self.stdout.write("Nenhum e-mail agendado pendente para envio no momento.")
            return

        for lib in liberacoes:
            sucesso = enviar_email_liberacao(lib.id)
            if sucesso:
                self.stdout.write(self.style.SUCCESS(f"E-mail da liberação {lib.id} enviado com sucesso."))
            else:
                self.stdout.write(self.style.ERROR(f"Falha ao enviar e-mail da liberação {lib.id}."))
