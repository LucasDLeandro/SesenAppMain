from django.http import HttpResponse
from django.shortcuts import render

from ..models.reg_os_model import ServiceOrder
from ..forms.create_os import CreateOsForm

def os_list(request):
    model = ServiceOrder
    
    if request.method == 'POST':
        form = CreateOsForm(request.POST)
        if form.is_valid():
            data_hora = form.cleaned_data['data_hora']
            return HttpResponse(f'Service Order created for {data_hora}')
    else:
        form = CreateOsForm()
    return render(request, 'ordens/create_os.html', {'form': form})