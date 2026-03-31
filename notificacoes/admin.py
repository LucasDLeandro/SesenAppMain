from django.contrib import admin

# Register your models here.
from .models.contato_notificacao import Contato
from .models.template_notificacao import TemplateMessage

admin.site.register(Contato)
admin.site.register(TemplateMessage)