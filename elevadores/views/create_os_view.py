from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from ..models.elev_so_model import ElevOrderReg
from ..forms.elev_os_form import ElevCreateOsForm
from notificacoes.services import auto_message

def create_os(request):
    if request.method == 'POST':
        form = ElevCreateOsForm(request.POST)
        if form.is_valid():
            ordem_servico = form.save()
            data_hora = form.cleaned_data['data_hora']
            messages.success(request, f'Ordem de Serviço {ordem_servico.protocolo} criada com sucesso!')

            # Só dispara notificação para OS's do dia atual
            hoje = timezone.localtime(timezone.now()).date()
            data_os = timezone.localtime(ordem_servico.data_hora).date() if ordem_servico.data_hora else None
            if data_os == hoje:
                try:
                    tel = "5561992425395"
                    text = f"""Prezados(as),\n\nSeguem as informações sobre a abertura do chamado para a empresa Otis:\n\nAtendente OTIS: {ordem_servico.atendente}\nData/Hora: {ordem_servico.data_hora}\nElevador: {ordem_servico.elevador}\nOcorrência: {ordem_servico.ocorrencia}\nProtocolo: {ordem_servico.protocolo}\nSolicitante: {ordem_servico.solicitante}"""
                    auto_message(tel, text)
                except Exception as e:
                    print(f"Erro na Evolution API: {e}")
                    messages.warning(request, "OS criada, mas erro ao enviar WhatsApp.")
        return redirect('ordens:create_os')
            
    else:
        form = ElevCreateOsForm()
    return render(request, 'ordens/create_os.html', {'form': form})