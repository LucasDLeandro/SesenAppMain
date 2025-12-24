from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from ..models.reg_os_model import ServiceOrder

def os_list(request):
    oss = ServiceOrder.objects.all()
    return render(request, 'ordens/listar_os.html', {'oss': oss})