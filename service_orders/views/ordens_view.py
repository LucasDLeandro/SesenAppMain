from django.shortcuts import render
from ..models.elev_so_model import ElevOrderReg

from ..filters.os_filter import OsFilter

def main_ordens(request):
    
    return render(request, 'ordens/base_ordens.html')