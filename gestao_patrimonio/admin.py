
from django.apps import apps
from django.contrib import admin

try:
    app_models = apps.get_app_config('gestao_patrimonio').get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
