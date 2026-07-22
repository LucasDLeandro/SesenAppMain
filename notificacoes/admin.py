from django.contrib import admin

# Register your models here.
from .models.contato_notificacao import Contato
from .models.template_notificacao import TemplateMessage

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'is_ativo')
    search_fields = ('nome', 'telefone')
    list_filter = ('is_ativo',)

@admin.register(TemplateMessage)
class TemplateMessageAdmin(admin.ModelAdmin):
    list_display = ('id_template', 'tipo_evento', 'is_ativo')
    search_fields = ('id_template', 'tipo_evento')
    list_filter = ('is_ativo',)