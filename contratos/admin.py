from django.contrib import admin

# Register your models here.
from .models.model_contratos import Contratos

@admin.register(Contratos)
class ContratosAdmin(admin.ModelAdmin):
    list_display = ('num_contrato', 'empresa', 'inicio_vigencia', 'termino_vigencia', 'valor')
    search_fields = ('num_contrato', 'empresa__nome')

from django.apps import apps

# Register ALL models from ALL apps dynamically
for model in apps.get_app_config('contratos').get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
