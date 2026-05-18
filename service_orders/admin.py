from django.contrib import admin


# Register your models here.
from .models.elev_so_model import ElevOrderReg
from .models.eng_reg_os_model import EngServiceReg
from .models.mapa_servicos import Categoria, Servico



admin.site.register(Categoria)
admin.site.register(Servico)
admin.site.register(EngServiceReg)

@admin.register(ElevOrderReg)
class ElevOrderRegAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'data_hora', 'ocorrencia', 'elevador_parado', 'data_hora_chegada', 'data_hora_conclusao', 'tempo_parado', 'elevador', 'tecnico', 'status')
    search_fields = ('protocolo', 'elevador', 'tecnico')

    list_filter = ('status', 'elevador_parado')

    ordering = ('-data_hora',)