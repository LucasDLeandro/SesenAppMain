from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from ..models.elevadores_reg_os_model import ElevOrderReg
from ..forms.elev_create_os import CreateOsForm

def create_os(request):
    if request.method == 'POST':
        form = CreateOsForm(request.POST)
        if form.is_valid():
            ordem_servico = form.save()
            data_hora = form.cleaned_data['data_hora']
            messages.success(request, f'Ordem de Serviço {ordem_servico.protocolo} criada com sucesso!')
            return redirect('ordens:create_os')
            
    else:
        form = CreateOsForm()
    return render(request, 'ordens/create_os.html', {'form': form})