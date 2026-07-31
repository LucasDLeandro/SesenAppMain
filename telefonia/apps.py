from django.apps import AppConfig


class TelefoniaConfig(AppConfig):
    name = 'telefonia'

    def ready(self):
        try:
            from . import scheduler
            scheduler.start()
        except ImportError:
            pass
