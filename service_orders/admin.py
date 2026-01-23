from django.contrib import admin


# Register your models here.
from .models.elevadores_reg_os_model import ElevOrderReg
from .models.elevadores_close_os_model import ElevOrderClose
from .models.mapa_servicos import Categoria, Servico

admin.site.register(ElevOrderReg)
admin.site.register(ElevOrderClose)
admin.site.register(Categoria)
admin.site.register(Servico)