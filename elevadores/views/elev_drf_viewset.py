from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import ElevConcluirOsSerializer, ElevRegistrarOsSerializer, DashboardFiltroSerializer, ElevadorSerializer


from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, ExpressionWrapper, DurationField, Count, Sum, Value, IntegerField, DecimalField, F
from django.db.models.functions import TruncMonth, TruncYear, TruncDate, Round
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from collections import defaultdict

from zoneinfo import ZoneInfo

from ..utils import calc_hrs_uteis_parado
from ..forms.elev_os_form import ElevCreateOsForm, ElevConcluirOsForm
from notificacoes.services import auto_message
from notificacoes.models.contato_notificacao import Contato
from notificacoes.models.template_notificacao import TemplateMessage
from ..models.elev_so_model import ElevOrderReg

from decimal import Decimal

import pandas as pd
from datetime import datetime, timedelta
import holidays


class ElevadorViewSet(viewsets.ModelViewSet):

    queryset = ElevOrderReg.objects.all()
    serializer_class = ElevadorSerializer

    def create(self, request):
        dados = request.data.copy()
        dados['status'] = 'ABERTA'

        serializer = ElevRegistrarOsSerializer(data=dados)

        serializer.is_valid(raise_exception=True)

        os_salva = serializer.save()

        if os_salva.elevador_parado == 'PARADO':
            from .models.elev_so_model import ElevadorStatus
            try:
                elev_status = ElevadorStatus.objects.get(elevador=os_salva.elevador)
                if elev_status.status != 'PARADO':
                    elev_status.status = 'PARADO'
                    elev_status.data_hora_parada = os_salva.data_hora
                    elev_status.save()
            except ElevadorStatus.DoesNotExist:
                pass

        self._disparar_notificacao(os_salva, 'os_elev_registro')

        return Response({
            'sucesso': True,
            'mensagem': f'Ordem de Serviço nº: {os_salva}, registrada com sucesso!'
        }, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['post'], url_path='concluir_elev_os')
    def elev_concluir_os(self, request, pk=None):
        os_existente = self.get_object()

        serializer = ElevConcluirOsSerializer(os_existente, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        os_salva = serializer.save()

        if os_salva.elevador_parado == 'PARADO':
            from .models.elev_so_model import ElevadorStatus
            try:
                elev_status = ElevadorStatus.objects.get(elevador=os_salva.elevador)
                # Verifica se não há OUTRA OS aberta e parada
                outras_paradas = ElevOrderReg.objects.filter(elevador=os_salva.elevador, status='ABERTA', elevador_parado='PARADO').exists()
                if not outras_paradas:
                    elev_status.status = 'ATIVO'
                    elev_status.data_hora_parada = None
                    elev_status.save()
            except ElevadorStatus.DoesNotExist:
                pass

        self._disparar_notificacao(os_salva, 'os_elev_conclusao')

        return Response({
            'sucesso': True,
            'mensagem': f'Ordem de Serviço: {os_salva.protocolo}, concluída com sucesso!'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='elev_oss_concluidas')
    def elev_oss_concluidas(self, request):
        ordens_concluidas_tabela = self.get_queryset().filter(status='CONCLUIDA').order_by('-data_hora').annotate(
        tmp_chegada = ExpressionWrapper(F('data_hora_chegada') - F('data_hora'), output_field=DurationField()),
        tmp_conclusao = ExpressionWrapper(F('data_hora_conclusao') - F('data_hora_chegada'), output_field=DurationField()),
        
        )

        concluidas_tabela = []

        for os in ordens_concluidas_tabela:
            min_chegada = int(os.tmp_chegada.total_seconds() / 60) if os.tmp_chegada else 0 # type: ignore
            min_saida = int(os.tmp_conclusao.total_seconds() / 60) if os.tmp_conclusao else 0 # type: ignore

            data_hora_local = timezone.localtime(os.data_hora) if os.data_hora else None
            chegada_local = timezone.localtime(os.data_hora_chegada) if os.data_hora_chegada else None
            conclusao_local = timezone.localtime(os.data_hora_conclusao) if os.data_hora_conclusao else None

            os_dict = {
                'protocolo': os.protocolo,
                'data_hora': data_hora_local.strftime('%d/%m/%Y %H:%M') if data_hora_local else '',
                'elevador': os.elevador,
                'ocorrencia': os.ocorrencia,
                'solicitante': os.solicitante,
                'tecnico': os.tecnico,
                'data_hora_chegada': chegada_local.strftime('%d/%m/%Y %H:%M') if chegada_local else '',
                'tmp_chegada': min_chegada, #type: ignore
                'data_hora_saida': conclusao_local.strftime('%d/%m/%Y %H:%M') if conclusao_local else '',
                'tmp_saida': min_saida, #type: ignore
                'tempo_parado': os.tempo_parado,
                'componente': 0,
                'sub_componente': 0,
                'servico': os.servico,
                'status': os.status,
            }
            

            concluidas_tabela.append(os_dict)

        return Response({'tabela_concluidas': concluidas_tabela}, status=status.HTTP_200_OK)

    def api_indicador_um(self, **kwargs):   
        indicador_um = []
        META_PP = 30.0
        META_COMUM = 120.0
        qs_filtrado = self.get_queryset().filter(status='CONCLUIDA', data_hora__range=(kwargs['inicio'], kwargs['fim'])).order_by('-data_hora').annotate(
            tmp_chegada = ExpressionWrapper(F('data_hora_chegada') - F('data_hora'), output_field=DurationField()),
            tmp_conclusao = ExpressionWrapper(F('data_hora_conclusao') - F('data_hora_chegada'), output_field=DurationField())
        )
            
        for os_i in qs_filtrado:
            min_chegada = int(os_i.tmp_chegada.total_seconds() / 60) if os_i.tmp_chegada else 0 # type: ignore
            os_dict = {
                'elevador': os_i.elevador,
                'data_hora': os_i.data_hora.strftime('%d/%m/%Y %H:%M'),
                'protocolo': os_i.protocolo,
                'min_chegada': min_chegada,
                'meta_pp': META_PP,
                'meta_comum': META_COMUM 
            }
            indicador_um.append(os_dict)

        return indicador_um
    
    def api_indicador_dois(self, **kwargs):
        from ..models import ManutencaoPreventiva
        from ..models.elev_so_model import ElevadorStatus
        
        elevadores_parados = set(ElevadorStatus.objects.filter(status='PARADO').values_list('elevador', flat=True))

        qs_filtrado = ManutencaoPreventiva.objects.filter(
            mes_referencia__range=(kwargs['inicio'], kwargs['fim'])
        )
        
        indicador_dois = []
        elevadores_processados = set()
        
        for mpm in qs_filtrado:
            status = 'PARADO' if mpm.elevador in elevadores_parados else mpm.status
            data_exec = '' if status == 'PARADO' else (mpm.data_execucao.strftime('%d/%m/%Y') if mpm.data_execucao else '')
            os_dict = {
                'elevador': mpm.elevador,
                'data_execucao': data_exec,
                'ordem_servico': mpm.ordem_servico or '',
                'tecnico': mpm.tecnico or '',
                'status': status,
            }
            indicador_dois.append(os_dict)
            elevadores_processados.add(mpm.elevador)
            
        for elev in elevadores_parados:
            if elev not in elevadores_processados:
                indicador_dois.append({
                    'elevador': elev,
                    'data_execucao': '',
                    'ordem_servico': '',
                    'tecnico': '',
                    'status': 'PARADO'
                })
                
        return indicador_dois
    
    def api_indicador_tres(self, **kwargs):
        indicador = self.get_queryset().filter(tipo_chamado='CORRETIVO', data_hora__range=(kwargs['inicio'], kwargs['fim'])).annotate(data_truncada=TruncDate('data_hora')).values('protocolo', 'elevador', 'data_truncada').annotate(ocorrencias=Count('id')).order_by('data_truncada')
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
        #df['elevador'] = pd.Categorical(df['elevador'], categories=listaElevadores)

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
    
    def api_indicador_quatro(self, **kwargs):
        from ..models.elev_so_model import ElevadorStatus, ElevadorParadaHistorico
        feriados_br = holidays.country_holidays('BR', language='pt_BR')
        from decimal import Decimal
        HRS_UTEIS_DIA = 12.0

        inicio = kwargs["inicio"]
        fim = kwargs["fim"]

        qnt_dias_uteis = feriados_br.get_working_days_count(inicio, fim)
        qnt_horas_uteis_totais = Decimal(str(HRS_UTEIS_DIA * qnt_dias_uteis))

        import datetime
        from django.utils import timezone
        
        def to_date(val):
            if isinstance(val, str):
                return datetime.datetime.strptime(val, '%Y-%m-%d').date()
            if isinstance(val, datetime.datetime):
                return val.date()
            if isinstance(val, datetime.date):
                return val
            return None

        def to_aware_datetime(val, end_of_day=False):
            if isinstance(val, str):
                val = datetime.datetime.strptime(val, '%Y-%m-%d')
            if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
                val = datetime.datetime.combine(val, datetime.time.min)
            if end_of_day:
                val = val.replace(hour=23, minute=59, second=59)
            if timezone.is_naive(val):
                val = timezone.make_aware(val)
            return val

        inicio_date = to_date(inicio)
        fim_dt = to_aware_datetime(fim, end_of_day=True)

        # Pega todos os elevadores que estão sendo monitorados e não estão desativados
        elevadores_ativos = ElevadorStatus.objects.exclude(status__in=['DESATIVADO', 'INATIVO'])
        
        dados_parada = {}
        for elev in elevadores_ativos:
            parada_date = to_date(elev.data_hora_parada)
            if elev.status in ['PARADO', 'PROGRAMADO'] and parada_date and parada_date < inicio_date:
                continue
                
            dados_parada[elev.elevador] = Decimal('0.0')
            
            if elev.status in ['PARADO', 'PROGRAMADO'] and parada_date and parada_date >= inicio_date:
                from elevadores.serializers import calc_hrs_uteis_parado
                end_stop = min(fim_dt, timezone.now())
                if elev.data_hora_parada < end_stop:
                    horas_paradas = calc_hrs_uteis_parado(elev.data_hora_parada, end_stop)
                    dados_parada[elev.elevador] += Decimal(str(horas_paradas))

        qs_os = self.get_queryset().filter(
            status='CONCLUIDA', data_hora__range=(inicio, fim)
        ).values('elevador').annotate(
            total_os=Sum('tempo_parado')
        )
        
        qs_hist = ElevadorParadaHistorico.objects.filter(
            data_hora_retorno__range=(inicio, fim)
        ).values('elevador').annotate(
            total_hist=Sum('tempo_parado')
        )
        
        for item in qs_os:
            elev_nome = item['elevador']
            if elev_nome in dados_parada:
                dados_parada[elev_nome] += item['total_os'] or Decimal('0.0')
            
        for item in qs_hist:
            elev_nome = item['elevador']
            if elev_nome in dados_parada:
                dados_parada[elev_nome] += item['total_hist'] or Decimal('0.0')
        
        ind_quatro = []
        for elev_nome, total_parado in dados_parada.items():
            hrs_disponivel = qnt_horas_uteis_totais - total_parado
            if qnt_horas_uteis_totais > 0:
                disp_bruta = (hrs_disponivel / qnt_horas_uteis_totais) * Decimal('100.0')
            else:
                disp_bruta = Decimal('0.0')
                
            disp_tratada = round(float(disp_bruta), 2)
            
            ind_quatro.append({
                "elevador": elev_nome,
                "tempo_parado": float(total_parado),
                "total_mes": float(qnt_horas_uteis_totais),
                "dias_uteis": qnt_dias_uteis,
                "horas_disponiveis": float(hrs_disponivel),
                "disponibilidade": disp_tratada
            })
            
        ind_quatro.sort(key=lambda x: x['elevador'])
        return ind_quatro
    
    def api_totalizacao_elev_grafico_qnt(self, **kwargs):
        ##########---------------------------------- GRÁFICO DE OCORRÊNCIAS E TOTALIZAÇÃO DE OCORRÊNCIAS ----------------------------------##########
        # listas vazias para receber os dados
        meses_labels = []
        totais_series = []
        tabela_mes_total = []
        
        # Filtro GROUP_BY para contagem das OSs 


        dados_total = self.get_queryset().annotate(mes_exato=TruncMonth('data_hora')).values('mes_exato').annotate(total_mes=Count('id')).order_by('mes_exato')
        dados_grafico_anual = self.get_queryset().annotate(mes_exato=TruncMonth('data_hora')).values('mes_exato').annotate(total_mes=Count('id')).order_by('mes_exato')

        df_grafico = pd.DataFrame(list(dados_grafico_anual))

        if df_grafico.empty:
            dados_vazios = [{'mes': [], 'quantidade': []}]
            return Response({'chart_qnt_anual': dados_vazios})
        
        
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
    
            return [
                meses_labels,
                totais_series,
                tabela_mes_total,
                df_html,
                dados_finais_grafico
                ]

    def _disparar_notificacao(self, os, evento):
        contato_queryset = Contato.objects.filter(is_ativo=True)
        if evento == 'os_elev_registro':
            template = get_object_or_404(TemplateMessage, tipo_evento=evento, is_ativo=True)
            texto = template.base_text
            for contato in contato_queryset:
                tel = contato.telefone
                text = texto.format(
                    nome=contato.nome,
                    atendente=os.atendente,
                    data_hora=os.data_hora.strftime("%d/%m/%Y às %H:%M"),
                    elevador=os.elevador,
                    ocorrencia=os.ocorrencia,
                    protocolo=os.protocolo,
                    solicitante=os.solicitante,
                )
                try:
                    auto_message(tel, text)
                except Exception as e:
                    print(f"Erro na Evolution API: {e}")
            if not template: 
                print("Erro: Template de conclusão não encontrado.")
                return
        else:
            template = get_object_or_404(TemplateMessage, tipo_evento='os_elev_conclusao', is_ativo=True)
            texto = template.base_text
            for contato in contato_queryset:
                tel = contato.telefone
                try: 
                    text = texto.format(
                        nome=contato.nome,
                        protocolo=os.protocolo,
                        elevador=os.elevador,
                        tecnico=os.tecnico,
                        data_hora_saida=os.data_hora_conclusao.strftime("%d/%m/%Y às %H:%M"),
                        servico=os.servico,
                        funcionando=os.elevador_parado
                    )
                    auto_message(tel, text)   
                except Exception as e:
                    print(f"Erro na Evolution API: {e}")
            if not template: 
                print("Erro: Template de conclusão não encontrado.")
                return
        
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        
        serializer = DashboardFiltroSerializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)

        filtros = serializer.validated_data # type: ignore

        ind_um = self.api_indicador_um(**filtros) # type: ignore
        ind_dois = self.api_indicador_dois(**filtros)
        ind_tres = self.api_indicador_tres(**filtros)
        ind_quatro = self.api_indicador_quatro(**filtros)
        totalizacao_elev = self.api_totalizacao_elev_grafico_qnt(**filtros)

        return Response({
            'ind_um': ind_um,
            'ind_dois': ind_dois,
            'ind_tres': ind_tres,
            'ind_quatro': ind_quatro,
            'totalizacao': totalizacao_elev
        })
        
    @action(detail=False, methods=['get', 'post'], url_path='status_elevadores')
    def status_elevadores(self, request):
        """Retorna o status em tempo real de cada elevador usando a model ElevadorStatus e permite atualizá-los."""
        from ..models.elev_so_model import ElevadorStatus, ElevadorParadaHistorico
        from django.utils import timezone
        import datetime
        from django.utils.dateparse import parse_datetime
        from elevadores.serializers import calc_hrs_uteis_parado
        from decimal import Decimal
        
        if request.method == 'POST':
            elevador_nome = request.data.get('elevador')
            novo_status = request.data.get('status')
            programacao = request.data.get('programacao', '')
            motivo = request.data.get('motivo', '')
            data_hora_parada_req = request.data.get('data_hora_parada')
            prog_inicio_req = request.data.get('programacao_inicio')
            prog_fim_req = request.data.get('programacao_fim')
            
            if elevador_nome and novo_status:
                try:
                    elev = ElevadorStatus.objects.get(elevador=elevador_nome)
                    
                    if novo_status != 'PARADO' and elev.status == 'PARADO' and elev.data_hora_parada:
                        data_hora_retorno = timezone.now()
                        tmp_parado = calc_hrs_uteis_parado(elev.data_hora_parada, data_hora_retorno)
                        
                        ElevadorParadaHistorico.objects.create(
                            elevador=elevador_nome,
                            data_hora_parada=elev.data_hora_parada,
                            data_hora_retorno=data_hora_retorno,
                            tempo_parado=Decimal(str(tmp_parado))
                        )

                    elev.status = novo_status
                    if novo_status == 'PROGRAMADO':
                        elev.programacao = programacao
                        elev.motivo_programacao = motivo
                        if prog_inicio_req:
                            dt_ini = parse_datetime(prog_inicio_req)
                            if dt_ini and timezone.is_naive(dt_ini):
                                dt_ini = timezone.make_aware(dt_ini)
                            elev.programacao_inicio = dt_ini
                        if prog_fim_req:
                            dt_fim = parse_datetime(prog_fim_req)
                            if dt_fim and timezone.is_naive(dt_fim):
                                dt_fim = timezone.make_aware(dt_fim)
                            elev.programacao_fim = dt_fim
                    else:
                        elev.programacao = ''
                        elev.motivo_programacao = ''
                        elev.programacao_inicio = None
                        elev.programacao_fim = None
                        
                    if novo_status == 'PARADO':
                        if data_hora_parada_req:
                            dt = parse_datetime(data_hora_parada_req)
                            if dt:
                                if timezone.is_naive(dt):
                                    dt = timezone.make_aware(dt)
                                elev.data_hora_parada = dt
                            else:
                                if not elev.data_hora_parada:
                                    elev.data_hora_parada = timezone.now()
                        else:
                            if not elev.data_hora_parada:
                                elev.data_hora_parada = timezone.now()
                    else:
                        elev.data_hora_parada = None
                        
                    elev.save()
                    return Response({'message': 'Status atualizado com sucesso.'}, status=status.HTTP_200_OK)
                except ElevadorStatus.DoesNotExist:
                    return Response({'error': 'Elevador não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        status_lista = []
        elevadores = ElevadorStatus.objects.all()
        for elev in elevadores:
            status_lista.append({
                'elevador': elev.elevador,
                'status': elev.status,
                'programacao': elev.programacao,
                'motivo': elev.motivo_programacao,
                'data_hora_abertura': elev.data_hora_parada.isoformat() if elev.data_hora_parada else None
            })
            
        return Response({'status_elevadores': status_lista}, status=status.HTTP_200_OK)

class ManutencaoPreventivaViewSet(viewsets.ModelViewSet):
    from ..models import ManutencaoPreventiva
    from ..serializers import ManutencaoPreventivaSerializer
    queryset = ManutencaoPreventiva.objects.all().order_by('-data_execucao', '-mes_referencia')
    serializer_class = ManutencaoPreventivaSerializer

class PecaManutencaoViewSet(viewsets.ModelViewSet):
    from ..models import PecaManutencao
    from ..serializers import PecaManutencaoSerializer
    queryset = PecaManutencao.objects.all().order_by('-data_registro')
    serializer_class = PecaManutencaoSerializer
        
       
        
# @require_POST
# def api_elev_criar_os(request):
#     requisicao = request.POST.copy()
#     requisicao["status"] = "ABERTA"
#     form = ElevCreateOsForm(requisicao)
#     if form.is_valid():
#         ordem_servico = form.save()
#         contato_queryset = Contato.objects.filter(is_ativo=True)
#         template = get_object_or_404(TemplateMessage, tipo_evento='os_elev_registro', is_ativo=True)
#         texto = template.base_text
#         for contato in contato_queryset:
#             tel = contato.telefone
#             text = texto.format(
#                 nome=contato.nome,
#                 atendente=ordem_servico.atendente,
#                 data_hora=ordem_servico.data_hora.strftime("%d/%m/%Y às %H:%M"),
#                 elevador=ordem_servico.elevador,
#                 ocorrencia=ordem_servico.ocorrencia,
#                 protocolo=ordem_servico.protocolo,
#                 solicitante=ordem_servico.solicitante,
#             )
#             try:
#                 auto_message(tel, text)
#             except Exception as e:
#                 print(f"Erro na Evolution API: {e}")
#         return JsonResponse({
#             'sucesso': True,
#             'mensagem': f'Ordem de Serviço nº: {ordem_servico.protocolo}, registrada com sucesso!'
#         })
#     return JsonResponse({
#         'sucesso': False,
#         'erros': form.errors
#     }, status=400)

# @require_POST
# def api_elev_concluir_os(request, id_elev_os):
#     os_existente = get_object_or_404(ElevOrderReg, pk=id_elev_os)
#     elev_parado = os_existente.elevador_parado
#     form = ElevConcluirOsForm(request.POST, instance=os_existente)
#     contato_queryset = Contato.objects.filter(is_ativo=True)

#     if form.is_valid():
#         if elev_parado == 'PARADO':
#             tmp_parado = calc_hrs_uteis_parado(os_existente.data_hora, form.cleaned_data["data_hora_conclusao"])
#             os_existente.tempo_parado = Decimal(str(tmp_parado))
#         else:
#             os_existente.tempo_parado = Decimal(str(0.0))
            
#         os = form.save()

#         template = get_object_or_404(TemplateMessage, tipo_evento='os_elev_conclusao', is_ativo=True)
#         if template: 
#             texto = template.base_text
#             for contato in contato_queryset:
#                 tel = contato.telefone
#                 try: 
#                     text = texto.format(
#                         nome=contato.nome,
#                         protocolo=os.protocolo,
#                         tecnico=os.tecnico,
#                         data_hora_saida=os.data_hora_conclusao.strftime("%d/%m/%Y às %H:%M"),
#                         servico=os.servico,
#                         funcionando=os.elevador_parado
#                     )
#                     auto_message(tel, text)   
#                 except Exception as e:
#                     print(f"Erro na Evolution API: {e}")
#         else:
#             print("Erro: Template de conclusão, não encontrado. Nenhuma notificação enviada.")

#         return JsonResponse({
#             'sucesso': True,
#             'mensagem': f'Ordem de Serviço: {os_existente.protocolo}, concluída com sucesso!'
#         })
#     return JsonResponse({
#         'sucesso': False,
#         'erros': form.errors
#     }, status=400)

# @require_GET
# def api_elev_concluidas(request):
#     ##############----------------TABELA OSS ELEVADOR CONCLUIDAS----------------##############
#     ordens_concluidas_tabela = ElevOrderReg.objects.filter(status='CONCLUIDA').order_by('-data_hora').annotate(
#         tmp_chegada = ExpressionWrapper(F('data_hora_chegada') - F('data_hora'), output_field=DurationField()),
#         tmp_conclusao = ExpressionWrapper(F('data_hora_conclusao') - F('data_hora_chegada'), output_field=DurationField()),
        
#     )

#     concluidas_tabela = []

#     for os in ordens_concluidas_tabela:
#         min_chegada = int(os.tmp_chegada.total_seconds() / 60) if os.tmp_chegada else 0 # type: ignore
#         min_saida = int(os.tmp_conclusao.total_seconds() / 60) if os.tmp_conclusao else 0 # type: ignore

#         data_hora_local = timezone.localtime(os.data_hora) if os.data_hora else None
#         chegada_local = timezone.localtime(os.data_hora_chegada) if os.data_hora_chegada else None
#         conclusao_local = timezone.localtime(os.data_hora_conclusao) if os.data_hora_conclusao else None

#         os_dict = {
#             'protocolo': os.protocolo,
#             'data_hora': data_hora_local.strftime('%d/%m/%Y %H:%M') if data_hora_local else '',
#             'elevador': os.elevador,
#             'ocorrencia': os.ocorrencia,
#             'solicitante': os.solicitante,
#             'tecnico': os.tecnico,
#             'data_hora_chegada': chegada_local.strftime('%d/%m/%Y %H:%M') if chegada_local else '',
#             'tmp_chegada': min_chegada, #type: ignore
#             'data_hora_saida': conclusao_local.strftime('%d/%m/%Y %H:%M') if conclusao_local else '',
#             'tmp_saida': min_saida, #type: ignore
#             'tempo_parado': os.tempo_parado,
#             'componente': 0,
#             'sub_componente': 0,
#             'servico': os.servico,
#             'status': os.status,
#         }
        

#         concluidas_tabela.append(os_dict)

#     return JsonResponse({'tabela_concluidas': concluidas_tabela})

# def api_dados_indicador_um(**kwargs):

#     indicador_um = []
#     META_PP = 30.0
#     META_COMUM = 120.0
#     qs_filtrado = ElevOrderReg.objects.filter(status='CONCLUIDA', data_hora__range=(kwargs['inicio'], kwargs['fim'])).order_by('-data_hora').annotate(
#         tmp_chegada = ExpressionWrapper(F('data_hora_chegada') - F('data_hora'), output_field=DurationField()),
#         tmp_conclusao = ExpressionWrapper(F('data_hora_conclusao') - F('data_hora_chegada'), output_field=DurationField())
#     )
        
#     for os_i in qs_filtrado:
#         min_chegada = int(os_i.tmp_chegada.total_seconds() / 60) if os_i.tmp_chegada else 0 # type: ignore
#         os_dict = {
#             'elevador': os_i.elevador,
#             'data_hora': os_i.data_hora.strftime('%d/%m/%Y %H:%M'),
#             'protocolo': os_i.protocolo,
#             'min_chegada': min_chegada,
#             'meta_pp': META_PP,
#             'meta_comum': META_COMUM 
#         }
#         indicador_um.append(os_dict)

#     return indicador_um

#     #return JsonResponse({'indicador_um': indicador_um})

# ##############----------------INDICADOR 3----------------##############
# def api_dados_indicador_tres (**kwargs):
#     indicador = ElevOrderReg.objects.annotate(data_truncada=TruncDate('data_hora')).values('protocolo', 'elevador', 'data_truncada').annotate(ocorrencias=Count(id)).order_by('data_truncada')
#     listaElevadores = [
#         "Social 1 - M2674",
#         "Social 2 - M2675",
#         "Social 3 - M2676",
#         "Social 4 - M2677",
#         "Social 5 - M2678",
#         "Serviço 6 - M2679",
#         "Privativo 7 - M2680",
#         "Social 8 - M2681",
#         "Social 9 - M2682",
#         "Privativo 10 - M2683",
#         "Social 11 - M2684",
#         "Social 12 - M2685",
#         "Social 13 - M2686",
#         "Serviço 14 - M2687",
#     ]

#     df = pd.DataFrame(list(indicador))

#     if df.empty:
#         # Montamos a estrutura vazia para não quebrar o front-end
#         dados_vazios = [{'name': elev, 'x': [], 'y': [], 'z': [], 'protocolo': []} for elev in listaElevadores]
#         return JsonResponse({'ind_tres': dados_vazios})

#     df['data_truncada'] = df['data_truncada'].astype(str)
#     df['tamanho_z'] = df['ocorrencias'] * 20
#     #df['elevador'] = pd.Categorical(df['elevador'], categories=listaElevadores)

#     df_agrupado = df.groupby('elevador', observed=False).agg({
#         'data_truncada': list,
#         'ocorrencias': list,
#         'tamanho_z': list,
#         'protocolo': list
#     }).reset_index()

#     df_agrupado.rename(columns={
#         'elevador': 'name',
#         'data_truncada': 'x',
#         'ocorrencias': 'y',
#         'tamanho_z': 'z',
#     }, inplace=True)

#     print(df_agrupado)

#     dados_finais = df_agrupado.to_dict('records')

#     return dados_finais

#     # return JsonResponse({
#     #     'ind_tres': dados_finais,
#     # })

# def api_dados_indicador_quatro(**kwargs): 
#     feriados_br = holidays.country_holidays('BR', language='pt_BR')
#     HRS_UTEIS_DIA = 12.0

#     inicio = kwargs["inicio"]
#     fim = kwargs["fim"]

#     qnt_dias_uteis = feriados_br.get_working_days_count(inicio, fim)
#     qnt_horas_uteis_totais = HRS_UTEIS_DIA * qnt_dias_uteis

#     qs_ind_quatro = ElevOrderReg.objects.filter(
#         status='CONCLUIDA', data_hora__range=(inicio, fim)
#         ).values(
#             'elevador' 
#         ).annotate(
#             total_hrs_uteis_parado=Sum('tempo_parado'),
#         ).annotate(
#             hrs_uteis_total_mes=Value(qnt_horas_uteis_totais, output_field=DecimalField()),
#             hrs_uteis_disponivel=Value(qnt_horas_uteis_totais, output_field=DecimalField()) - F('total_hrs_uteis_parado'),
#         ).annotate(
#             disponibilidade=ExpressionWrapper((F('hrs_uteis_disponivel') / F('hrs_uteis_total_mes')) * 100.0, output_field=DecimalField())
#         ).order_by('elevador')
    
    
#     ind_quatro = []
#     for elev in qs_ind_quatro:
#         disp_bruta = elev["disponibilidade"]

#         disp_tratada = round(float(disp_bruta), 2) if disp_bruta is not None else 0.0
        
#         elev_dict = {
#             "elevador": elev["elevador"],
#             "tempo_parado": elev["total_hrs_uteis_parado"],
#             "total_mes": elev["hrs_uteis_total_mes"],
#             "dias_uteis": qnt_dias_uteis,
#             "horas_disponiveis": elev["hrs_uteis_disponivel"],
#             "disponibilidade": disp_tratada
#         }
#         ind_quatro.append(elev_dict)
    

#     return ind_quatro

# def api_grafico_qnt(**kwargs):
# ##########---------------------------------- GRÁFICO DE OCORRÊNCIAS E TOTALIZAÇÃO DE OCORRÊNCIAS ----------------------------------##########
#     # listas vazias para receber os dados
#     meses_labels = []
#     totais_series = []
#     tabela_mes_total = []
    
#     # Filtro GROUP_BY para contagem das OSs 


#     dados_total = ElevOrderReg.objects.all().annotate(mes_exato=TruncMonth('data_hora')).values('mes_exato').annotate(total_mes=Count('id')).order_by('mes_exato')
#     dados_grafico_anual = ElevOrderReg.objects.annotate(mes_exato=TruncMonth('data_hora')).values('mes_exato').annotate(total_mes=Count('id')).order_by('mes_exato')

#     df_grafico = pd.DataFrame(list(dados_grafico_anual))

#     if df_grafico.empty:
#         dados_vazios = [{'mes': [], 'quantidade': []}]
#         return JsonResponse({'chart_qnt_anual': dados_vazios})
    
    
#     df_grafico['mes_exato'] = df_grafico['mes_exato'].astype(str)

#     dados_finais_grafico = df_grafico.to_dict('list')
#     # Dicionário que mapeia as colunas do dataframe que representa a Totalização de Ocorrências
#     meses_list = {
#         'ano': 'Ano',
#         1: 'Janeiro',
#         2: 'Fevereiro',
#         3: 'Março',
#         4: 'Abril',
#         5: 'Maio',
#         6: 'Junho',
#         7: 'Julho',
#         8: 'Agosto',
#         9: 'Setembro',
#         10: 'Outubro',
#         11: 'Novembro',
#         12: 'Dezembro'
#     }

#     # Esse loop, prepara os dados, para a criação do dataframe
#     lista_temporaria = []
#     for item in dados_total:
#         lista_temporaria.append({
#             'ano': item['mes_exato'].year,
#             'mes': item['mes_exato'].month,
#             'mes_total': item['total_mes']
#         })

#     # Aqui o dataframe é criado e configurado
#     df = pd.DataFrame(lista_temporaria)
#     df['mes_total'] = df['mes_total'].astype('Int64').fillna(0)
#     df['mes_total_str'] = df['mes_total'].replace(0, '')

#     df_pivot = df.pivot(index='ano', columns='mes', values='mes_total').astype('Int64')
#     df_pivot['Total'] = df_pivot.sum(axis=1)
#     df_pivot = df_pivot.astype(object).fillna('-')
#     df_pivot.columns.name=None
#     df_pivot = df_pivot.reset_index()
#     df_pivot = df_pivot.rename(columns=meses_list)
    
#     # Aqui, o dataframe pivotado é convertido em html, para ser enviado em formato JSON via API
#     if not df.empty:
#         df_html = df_pivot.to_html(
#             classes=["table", "table-hover", "custom-modern-table", "table-compacta", "w-100"],
#             index=False,
#             justify="left",
#             table_id="tabela-cont-os-elev"
#         )
#     else:
#         df_html = "<p>Nenhuma OS encontrada.</p>"
    
#     # Esse loop for, gera os dados que serão aplicados ao "Gráfico de Ocorrências"
#     for item_mes in dados_grafico_anual:
#         mes = item_mes['mes_exato']
#         if mes: 
#             mes_formatado = mes.strftime('%m/%Y')
#         else:
#             mes_formatado = ""
#         totais_dict = {
#             'mes': mes_formatado, #type: ignore
#             'tot_mes': item_mes['total_mes'], #type: ignore
#         }


#         tabela_mes_total.append(totais_dict)
#         meses_labels.append(mes_formatado)
#         totais_series.append(item_mes['total_mes'])

        

# ##########---------------------------------- GRÁFICO DE OCORRÊNCIAS E TOTALIZAÇÃO DE OCORRÊNCIAS ----------------------------------##########
   
#         return [
#             meses_labels,
#             totais_series,
#             tabela_mes_total,
#             df_html,
#             dados_finais_grafico
#             ]
    
# @require_GET
# def api_elev_dashboard(request):
#     params_request = ['inicio', 'fim', 'ano', 'mes', 'dia', 'elev']
#     filtros = {chave: request.GET.get(chave) for chave in params_request if request.GET.get(chave)}

#     if 'inicio' in filtros:
#         inicio_dt = datetime.strptime(filtros['inicio'], '%Y-%m-%d')
#         filtros['inicio'] = timezone.make_aware(inicio_dt)
    
#     if 'fim' in filtros:
#         fim_dt = datetime.strptime(filtros['fim'], '%Y-%m-%d')
#         filtros['fim'] = timezone.make_aware(fim_dt)

#     ind_um = api_dados_indicador_um(**filtros)
#     #indicador_dois = 
#     ind_tres = api_dados_indicador_tres(**filtros)
#     ind_quatro = api_dados_indicador_quatro(**filtros)

#     totalizacao_elev = api_grafico_qnt(**filtros)

#     return JsonResponse({
#         'ind_um': ind_um,
#         'ind_tres': ind_tres,
#         'ind_quatro': ind_quatro,
#         'totalizacao': totalizacao_elev
#     })

    
    
    

