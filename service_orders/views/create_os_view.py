from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from ..models.elevadores_reg_os_model import ElevOrderReg
from ..forms.elev_create_os import CreateOsForm
from ..services import auto_message

def create_os(request):
    if request.method == 'POST':
        form = CreateOsForm(request.POST)
        if form.is_valid():
            ordem_servico = form.save()
            data_hora = form.cleaned_data['data_hora']
            messages.success(request, f'Ordem de Serviço {ordem_servico.protocolo} criada com sucesso!')
            try:
                tel = "5561992425395"
                text = f"""Prezados(as),\n\nSeguem as informações sobre a abertura do chamado para a empresa Otis:\n\nAtendente OTIS: {ordem_servico.atendente}\nData/Hora: {ordem_servico.data_hora}\nElevador: {ordem_servico.elevador}\nOcorrência: {ordem_servico.ocorrencia}\nProtocolo: {ordem_servico.protocolo}\nSolicitante: {ordem_servico.solicitante}"""
                auto_message(tel, text)
            except Exception as e:
                print(f"Erro na Evolution API: {e}")
                messages.warning(request, "OS criada, mas erro ao enviar WhatsApp.")
        return redirect('ordens:create_os')
            
    else:
        form = CreateOsForm()
    return render(request, 'ordens/create_os.html', {'form': form})