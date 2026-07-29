from django.contrib import admin
from .models import ProcessoSEI, HistoricoAndamento

@admin.register(ProcessoSEI)
class ProcessoSEIAdmin(admin.ModelAdmin):
    list_display = ('numero_processo', 'tipo', 'tempo_tramitacao', 'ultima_sincronizacao', 'contrato', 'empresa')
    list_filter = ('tipo', 'empresa', 'contrato')
    search_fields = ('numero_processo', 'objeto', 'situacao_atual')

@admin.register(HistoricoAndamento)
class HistoricoAndamentoAdmin(admin.ModelAdmin):
    list_display = ('processo', 'id_andamento_sei', 'data_hora', 'unidade', 'usuario')
    search_fields = ('processo__numero_processo', 'descricao')
    list_filter = ('data_hora',)
