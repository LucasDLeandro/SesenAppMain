from django.contrib import admin


# Register your models here.
from .models.elev_so_model import ElevOrderReg, ElevadorStatus, PecaManutencao
from .models.mapa_servicos import Categoria



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria',)
    search_fields = ('nome_categoria',)

# Removidos do admin: Servico e EngServiceReg
@admin.register(ElevOrderReg)
class ElevOrderRegAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'data_hora', 'ocorrencia', 'elevador_parado', 'data_hora_chegada', 'data_hora_conclusao', 'tempo_parado', 'elevador', 'tecnico', 'status')
    search_fields = ('protocolo', 'elevador', 'tecnico')

    list_filter = ('status', 'elevador_parado')

    ordering = ('-data_hora',)

@admin.register(ElevadorStatus)
class ElevadorStatusAdmin(admin.ModelAdmin):
    list_display = ('elevador', 'status', 'data_hora_parada')
    list_filter = ('status',)
    search_fields = ('elevador',)

from django.apps import apps

@admin.register(PecaManutencao)
class PecaManutencaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'elevador', 'tipo_peca', 'status', 'tecnico', 'data_registro', 'data_efetiva_troca')
    list_filter = ('status', 'elevador')
    search_fields = ('id', 'tipo_peca', 'tecnico', 'ordem_servico')

# Register all other models dynamically
app_models = apps.get_app_config('elevadores').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
