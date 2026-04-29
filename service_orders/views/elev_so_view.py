from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, ExpressionWrapper, DurationField, Count
from django.db.models.functions import TruncMonth, TruncYear, TruncDate
from django.utils.formats import date_format
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from collections import defaultdict

from zoneinfo import ZoneInfo


from ..forms.elev_os_form import ElevCreateOsForm, ElevConcluirOsForm
from notificacoes.services import auto_message
from notificacoes.models.contato_notificacao import Contato
from notificacoes.models.template_notificacao import TemplateMessage
from ..models.elev_so_model import ElevOrderReg

import pandas as pd
import datetime as dt



@require_POST
def api_elev_criar_os(request):
    form = ElevCreateOsForm(request.POST)

    if form.is_valid():
        ordem_servico = form.save()
        contato_queryset = Contato.objects.filter(is_ativo=True)
        template = get_object_or_404(TemplateMessage, tipo_evento='os_elev_registro', is_ativo=True)
        texto = template.base_text
        for contato in contato_queryset:
            tel = contato.telefone
            text = texto.format(
                nome=contato.nome,
                atendente=ordem_servico.atendente,
                data_hora=ordem_servico.data_hora.strftime("%d/%m/%Y às %H:%M"),
                elevador=ordem_servico.elevador,
                ocorrencia=ordem_servico.ocorrencia,
                protocolo=ordem_servico.protocolo,
                solicitante=ordem_servico.solicitante,
            )
            try:
                auto_message(tel, text)
            except Exception as e:
                print(f"Erro na Evolution API: {e}")
        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Ordem de Serviço nº: {ordem_servico.protocolo}, registrada com sucesso!'
        })
    return JsonResponse({
        'sucesso': False,
        'erros': form.errors
    }, status=400)
        
@require_POST
def api_elev_concluir_os(request, id_elev_os):
    os_existente = get_object_or_404(ElevOrderReg, pk=id_elev_os)
    form = ElevConcluirOsForm(request.POST, instance=os_existente)
    contato_queryset = Contato.objects.filter(is_ativo=True)

    if form.is_valid():
        os = form.save()
        

        for contato in contato_queryset:
            tel = contato.telefone
            
            try:
                template = get_object_or_404(TemplateMessage, tipo_evento='os_elev_conclusao', is_ativo=True)
                texto = template.base_text
                text = texto.format(
                    nome=contato.nome,
                    protocolo=os.protocolo,
                    tecnico=os.tecnico,
                    data_hora_saida=os.data_hora_saida.strftime("%d/%m/%Y às %H:%M"),
                    servico=os.servico,
                    funcionando=os.elevador_parado
                )
                auto_message(tel, text)   
            except Exception as e:
                print(f"Erro na Evolution API: {e}")

        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Ordem de Serviço: {os_existente.protocolo}, concluída com sucesso!'
        })
    return JsonResponse({
        'sucesso': False,
        'erros': form.errors
    }, status=400)


##############----------------INDICADOR 1----------------##############

@require_GET
def api_elev_concluidas(request):
    ##############----------------TABELA OSS ELEVADOR CONCLUIDAS----------------##############
    ordens_concluidas_tabela = ElevOrderReg.objects.filter(status='CONCLUIDA').order_by('-data_hora').annotate(
        tmp_chegada = ExpressionWrapper(F('data_hora_chegada') - F('data_hora'), output_field=DurationField()),
        tmp_conclusao = ExpressionWrapper(F('data_hora_saida') - F('data_hora_chegada'), output_field=DurationField())
    )

    concluidas_tabela = []

    for os in ordens_concluidas_tabela:
        min_chegada = int(os.tmp_chegada.total_seconds() / 60) if os.tmp_chegada else 0 # type: ignore
        min_saida = int(os.tmp_conclusao.total_seconds() / 60) if os.tmp_conclusao else 0 # type: ignore

        os_dict = {
            'protocolo': os.protocolo,
            'data_hora': os.data_hora.strftime('%d/%m/%Y %H:%M'),
            'elevador': os.elevador,
            'ocorrencia': os.ocorrencia,
            'solicitante': os.solicitante,
            'tecnico': os.tecnico,
            'data_hora_chegada': os.data_hora_chegada.strftime('%d/%m/%Y %H:%M') if os.data_hora_chegada else 0,
            'tmp_chegada': min_chegada, #type: ignore
            'data_hora_saida': os.data_hora_saida.strftime('%d/%m/%Y %H:%M') if os.data_hora_saida else 0,
            'tmp_saida': min_saida, #type: ignore
            'componente': 0,
            'sub_componente': 0,
            'servico': os.servico,
            'status': os.status,
        }

        concluidas_tabela.append(os_dict)

    return JsonResponse({'tabela_concluidas': concluidas_tabela})



def api_dados_indicador_um(**kwargs):

    indicador_um = []

    qs_filtrado = ElevOrderReg.objects.filter(status='CONCLUIDA', data_hora__range=(kwargs['inicio'], kwargs['fim'])).order_by('-data_hora').annotate(
        tmp_chegada = ExpressionWrapper(F('data_hora_chegada') - F('data_hora'), output_field=DurationField()),
        tmp_conclusao = ExpressionWrapper(F('data_hora_saida') - F('data_hora_chegada'), output_field=DurationField())
    )
        
    for os_i in qs_filtrado:
        min_chegada = int(os_i.tmp_chegada.total_seconds() / 60) if os_i.tmp_chegada else 0 # type: ignore
        os_dict = {
            'data_hora': os_i.data_hora,
            'protocolo': os_i.protocolo,
            'min_chegada': min_chegada,
        }
        indicador_um.append(os_dict)

    return indicador_um

    #return JsonResponse({'indicador_um': indicador_um})

##############----------------INDICADOR 3----------------##############
def api_dados_indicador_tres (**kwargs):
    indicador = ElevOrderReg.objects.annotate(data_truncada=TruncDate('data_hora')).values('protocolo', 'elevador', 'data_truncada').annotate(ocorrencias=Count(id)).order_by('data_truncada')
    listaElevadores = [
        "Social 1 - M2674",
        "Social 2 - M2675",
        "Social 3 - M2676",
        "Social 4 - M2677",
        "Social 5 - M2678",
        "Serviço 6 - M2679",
        "Privativo 7 - M2680",
        "Social 8 - M2681",
        "Social 9 - M2682",
        "Privativo 10 - M2683",
        "Social 11 - M2684",
        "Social 12 - M2685",
        "Social 13 - M2686",
        "Serviço 14 - M2687",
    ]

    df = pd.DataFrame(list(indicador))

    if df.empty:
        # Montamos a estrutura vazia para não quebrar o front-end
        dados_vazios = [{'name': elev, 'x': [], 'y': [], 'z': [], 'protocolo': []} for elev in listaElevadores]
        return JsonResponse({'ind_tres': dados_vazios})

    df['data_truncada'] = df['data_truncada'].astype(str)
    df['tamanho_z'] = df['ocorrencias'] * 20
    df['elevador'] = pd.Categorical(df['elevador'], categories=listaElevadores)

    df_agrupado = df.groupby('elevador', observed=False).agg({
        'data_truncada': list,
        'ocorrencias': list,
        'tamanho_z': list,
        'protocolo': list
    }).reset_index()

    df_agrupado.rename(columns={
        'elevador': 'name',
        'data_truncada': 'x',
        'ocorrencias': 'y',
        'tamanho_z': 'z',
    }, inplace=True)

    dados_finais = df_agrupado.to_dict('records')

    return dados_finais

    # return JsonResponse({
    #     'ind_tres': dados_finais,
    # })



def api_grafico_qnt(**kwargs):
##########---------------------------------- GRÁFICO DE OCORRÊNCIAS E TOTALIZAÇÃO DE OCORRÊNCIAS ----------------------------------##########
    # listas vazias para receber os dados
    meses_labels = []
    totais_series = []
    tabela_mes_total = []
    
    # Filtro GROUP_BY para contagem das OSs 
    dados_total = ElevOrderReg.objects.annotate(mes_exato=TruncMonth('data_hora')).values('mes_exato').annotate(total_mes=Count('id')).order_by('mes_exato')
    dados_grafico_anual = ElevOrderReg.objects.annotate(mes_exato=TruncMonth('data_hora')).values('mes_exato').annotate(total_mes=Count('id')).order_by('mes_exato')

    df_grafico = pd.DataFrame(list(dados_grafico_anual))

    if df_grafico.empty:
        dados_vazios = [{'mes': [], 'quantidade': []}]
        return JsonResponse({'chart_qnt_anual': dados_vazios})
    
    
    df_grafico['mes_exato'] = df_grafico['mes_exato'].astype(str)

    dados_finais_grafico = df_grafico.to_dict('list')
    # Dicionário que mapeia as colunas do dataframe que representa a Totalização de Ocorrências
    meses_list = {
        'ano': 'Ano',
        1: 'Janeiro',
        2: 'Fevereiro',
        3: 'Março',
        4: 'Abril',
        5: 'Maio',
        6: 'Junho',
        7: 'Julho',
        8: 'Agosto',
        9: 'Setembro',
        10: 'Outubro',
        11: 'Novembro',
        12: 'Dezembro'
    }

    # Esse loop, prepara os dados, para a criação do dataframe
    lista_temporaria = []
    for item in dados_total:
        lista_temporaria.append({
            'ano': item['mes_exato'].year,
            'mes': item['mes_exato'].month,
            'mes_total': item['total_mes']
        })

    # Aqui o dataframe é criado e configurado
    df = pd.DataFrame(lista_temporaria)
    df['mes_total'] = df['mes_total'].astype('Int64').fillna(0)
    df['mes_total_str'] = df['mes_total'].replace(0, '')

    df_pivot = df.pivot(index='ano', columns='mes', values='mes_total').astype('Int64')
    df_pivot['Total'] = df_pivot.sum(axis=1)
    df_pivot = df_pivot.astype(object).fillna('-')
    df_pivot.columns.name=None
    df_pivot = df_pivot.reset_index()
    df_pivot = df_pivot.rename(columns=meses_list)
    
    # Aqui, o dataframe pivotado é convertido em html, para ser enviado em formato JSON via API
    if not df.empty:
        df_html = df_pivot.to_html(
            classes=["table", "table-hover", "custom-modern-table", "table-compacta", "w-100"],
            index=False,
            justify="left",
            table_id="tabela-cont-os-elev"
        )
    else:
        df_html = "<p>Nenhuma OS encontrada.</p>"
    
    # Esse loop for, gera os dados que serão aplicados ao "Gráfico de Ocorrências"
    for item_mes in dados_grafico_anual:
        mes = item_mes['mes_exato']
        if mes: 
            mes_formatado = mes.strftime('%m/%Y')
        else:
            mes_formatado = ""
        totais_dict = {
            'mes': mes_formatado, #type: ignore
            'tot_mes': item_mes['total_mes'], #type: ignore
        }


        tabela_mes_total.append(totais_dict)
        meses_labels.append(mes_formatado)
        totais_series.append(item_mes['total_mes'])

        
##########---------------------------------- GRÁFICO DE OCORRÊNCIAS E TOTALIZAÇÃO DE OCORRÊNCIAS ----------------------------------##########
    return JsonResponse({
        'meses': meses_labels,
        'series': totais_series,
        'tabela_mes': tabela_mes_total,
        'df_html': df_html,
        'dados_grafico': dados_finais_grafico
    })

@require_GET
def api_elev_dashboard(request):
    params_request = ['inicio', 'fim', 'ano', 'mes', 'dia', 'elev',
    ]
    filtros = {chave: request.GET.get(chave) for chave in params_request if request.GET.get(chave)}

    ind_um = api_dados_indicador_um(**filtros)
    #indicador_dois = 
    ind_tres = api_dados_indicador_tres(**filtros)
    #indicador_quatro = 

    #totalizacao_elev = 

    return JsonResponse({
        'ind_um': ind_um,
        'ind_tres': ind_tres
    })

    
    
    

