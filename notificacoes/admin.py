from django.contrib import admin

# Register your models here.
from .models.contato_notificacao import Contato
from .models.template_notificacao import TemplateMessage

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'is_ativo')
    search_fields = ('pessoa__nome', 'pessoa__telefone')
    list_filter = ('is_ativo',)

@admin.register(TemplateMessage)
class TemplateMessageAdmin(admin.ModelAdmin):
    list_display = ('id_template', 'tipo_evento', 'is_ativo')
    search_fields = ('id_template', 'tipo_evento')
    list_filter = ('is_ativo',)
from django.apps import apps
from django.contrib import admin

try:
    app_models = apps.get_app_config('notificacoes').get_models()
    for model in app_models:
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass
except Exception:
    pass
