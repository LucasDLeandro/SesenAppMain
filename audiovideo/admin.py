from django.contrib import admin
from .models import EquipamentoAV, EventoAV, OrdemServicoAV

@admin.register(EquipamentoAV)
class EquipamentoAVAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'marca', 'patrimonio', 'numero_serie', 'status')
    search_fields = ('nome', 'patrimonio', 'numero_serie', 'marca')
    list_filter = ('status', 'categoria')
    ordering = ('nome',)

@admin.register(EventoAV)
class EventoAVAdmin(admin.ModelAdmin):
    list_display = ('nome', 'solicitante', 'local', 'data_inicio', 'data_fim', 'status')
    search_fields = ('nome', 'solicitante', 'local')
    list_filter = ('status', 'data_inicio')
    ordering = ('-data_inicio',)
    filter_horizontal = ('equipamentos_alocados',)

@admin.register(OrdemServicoAV)
class OrdemServicoAVAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'equipamento', 'tecnico', 'data_abertura', 'status')
    search_fields = ('protocolo', 'equipamento__nome', 'tecnico')
    list_filter = ('status', 'data_abertura')
    ordering = ('-data_abertura',)

from django.apps import apps
from django.contrib import admin

try:
    app_models = apps.get_app_config('audiovideo').get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
