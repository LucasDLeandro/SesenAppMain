from django.apps import AppConfig


class AdmSetupConfig(AppConfig):
    name = 'adm_setup'

    def ready(self):
        from . import signals
