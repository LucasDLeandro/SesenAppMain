from django.contrib import admin


# Register your models here.
from .models.elev_so_model import ElevOrderReg
from .models.eng_reg_os_model import EngServiceReg
from .models.mapa_servicos import Categoria, Servico

admin.site.register(ElevOrderReg)

admin.site.register(Categoria)
admin.site.register(Servico)
admin.site.register(EngServiceReg)