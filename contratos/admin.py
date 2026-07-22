from django.contrib import admin

# Register your models here.
from .models.model_contratos import Contratos

@admin.register(Contratos)
class ContratosAdmin(admin.ModelAdmin):
    list_display = ('num_contrato', 'empresa', 'inicio_vigencia', 'termino_vigencia', 'valor')
    search_fields = ('num_contrato', 'empresa__nome')
