from django.core.management.base import BaseCommand
from telefonia.tasks import verificar_e_notificar_eventos

class Command(BaseCommand):
    help = 'Notifica contatos de telefonia sobre equipamentos de eventos que precisam ser recolhidos hoje.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Executando verificar_e_notificar_eventos..."))
        verificar_e_notificar_eventos()
        self.stdout.write(self.style.SUCCESS("Concluído."))
