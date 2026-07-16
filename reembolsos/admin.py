from django.contrib import admin
from .models import LimiteReembolso, ServidorReembolso, SolicitacaoReembolso

@admin.register(LimiteReembolso)
class LimiteReembolsoAdmin(admin.ModelAdmin):
    list_display = ('indice', 'cargo', 'valor')
    search_fields = ('cargo',)
    ordering = ('indice',)

@admin.register(ServidorReembolso)
class ServidorReembolsoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'cargo_limite', 'telefone_linha', 'banco', 'criado_em')
    search_fields = ('nome', 'cpf')
    list_filter = ('cargo_limite',)
    ordering = ('nome',)

@admin.register(SolicitacaoReembolso)
class SolicitacaoReembolsoAdmin(admin.ModelAdmin):
    list_display = ('id', 'servidor', 'periodo_inicio', 'periodo_fim', 'valor_ressarcido', 'status')
    search_fields = ('servidor__nome', 'servidor__cpf')
    list_filter = ('status',)
    ordering = ('-criado_em',)
