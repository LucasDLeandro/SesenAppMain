from django.contrib import admin

from .models import ConfiguracaoGeral

@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
    list_display = ('notificar_novos_usuarios',)
