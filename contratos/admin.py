from django.contrib import admin

# Register your models here.
from .models.model_contratos import Contratos

admin.site.register(Contratos)
