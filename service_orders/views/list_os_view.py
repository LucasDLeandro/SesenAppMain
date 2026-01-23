from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from ..models.elevadores_reg_os_model import ElevOrderReg

from ..filters.os_filter import OsFilter

def list_os(request):
    f = OsFilter(request.GET, queryset=ElevOrderReg.objects.all())
    
    context = {
        'filter': f,
        'service_orders': f.qs
    }

    return render(request, 'ordens/listar_os.html', context)