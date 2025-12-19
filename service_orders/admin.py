from django.contrib import admin


# Register your models here.
from .models.reg_os_model import ServiceOrder
from .models.close_os_model import CloseOs

admin.site.register(ServiceOrder)
admin.site.register(CloseOs)