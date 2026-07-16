from django.contrib import admin


# Register your models here.
from .models.elev_so_model import ElevOrderReg, ElevadorStatus
from .models.eng_reg_os_model import EngServiceReg
from .models.mapa_servicos import Categoria, Servico



@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria',)
    search_fields = ('nome_categoria',)

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome_servico', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nome_servico',)

@admin.register(EngServiceReg)
class EngServiceRegAdmin(admin.ModelAdmin):
    list_display = ('os_id', 'categoria', 'servico', 'local', 'data_hora_atendimento', 'tecnico_responsavel')
    list_filter = ('categoria', 'servico', 'data_hora_atendimento')
    search_fields = ('os_id', 'descricao', 'local', 'tecnico_responsavel')
    ordering = ('-data_hora_atendimento',)
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