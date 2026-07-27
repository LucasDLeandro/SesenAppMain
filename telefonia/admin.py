from django.contrib import admin

# Register your models here.
from .models.solicitacao_aparelho import TelefoneSolicitacao
from .models.aparelhos_telefonicos import AparelhoVoip
from .models.remessa_manutencao import RemessaManutencao
from .models.solicitacao_senha import CriarSenha

@admin.register(TelefoneSolicitacao)
class TelefoneSolicitacaoAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'solicitante', 'ramal', 'local', 'status', 'data')
    search_fields = ('protocolo', 'solicitante', 'ramal')
    list_filter = ('status',)

@admin.register(AparelhoVoip)
class AparelhoVoipAdmin(admin.ModelAdmin):
    list_display = ('patrimonio', 'modelo', 'ramal', 'sala', 'status')
    search_fields = ('patrimonio', 'ramal')
    list_filter = ('status', 'modelo')

@admin.register(RemessaManutencao)
class RemessaManutencaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'memorando', 'empresa_contratada', 'data_remessa')
    search_fields = ('memorando', 'empresa_contratada')

@admin.register(CriarSenha)
class CriarSenhaAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'usuario', 'ramal', 'status', 'created_at')
    search_fields = ('protocolo', 'ramal', 'primeiro_nome')
    list_filter = ('status',)
from django.apps import apps
from django.contrib import admin

try:
    app_models = apps.get_app_config('telefonia').get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
