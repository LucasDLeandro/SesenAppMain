import pandas as pd
from django.shortcuts import render

from ..models.elev_so_model import ElevOrderReg, PecaManutencao
from ..forms.elev_os_form import ElevCreateOsForm, ElevConcluirOsForm

from ..filters.os_filter import OsFilter

def elev_list_os(request):
    f = OsFilter(request.GET, queryset=ElevOrderReg.objects.all().order_by('-data_hora'))
    elevCriarOsForm = ElevCreateOsForm()
    elevConcluirOsForm = ElevConcluirOsForm()
    ordens_abertas = ElevOrderReg.objects.filter(status='ABERTA').order_by('-data_hora')
    pecas_pendentes = PecaManutencao.objects.filter(status='PENDENTE').order_by('data_previsao_troca')

    ordens = ElevOrderReg.objects.filter(status='CONCLUIDA').values(
        'protocolo',
        'data_hora',
        'elevador',
        'ocorrencia',
        'aprisionamento',
        'servico',
        'tecnico',
        'data_hora_chegada',
        'data_hora_conclusao',
        'status'
    ).order_by('-data_hora')

    df = pd.DataFrame(list(ordens))
    
    if not df.empty:
        tabela_html = df.to_html(
            classes=["table", "table-striped", "table-bordered"],
            index=False,
            justify="left"
        )
    else:
        tabela_html = "<p>Nenhuma OS encontrada.</p>"
    


    
    context = {
        'filter': f,
        'service_orders': f.qs,
        'ordem': elevCriarOsForm,
        'ordem_concluir': elevConcluirOsForm,
        'pandas_df': tabela_html,
        'ordens_abertas': ordens_abertas,
        'pecas_pendentes': pecas_pendentes,
    }

    return render(request, 'ordens/elev_list_os.html', context)


