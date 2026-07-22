from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers import ElevConcluirOsSerializer, ElevRegistrarOsSerializer, DashboardFiltroSerializer, ElevadorSerializer, AlarmeEmsEventSerializer


from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, ExpressionWrapper, DurationField, Count, Sum, Value, IntegerField, DecimalField, Q
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
from empresas.models import Empresa, ContatoEmpresa
from contratos.models.model_contratos import Contratos
from django.contrib.auth.models import User
from ..models.elev_so_model import AlarmeEmsEvent

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
            from ..models.elev_so_model import ElevadorStatus
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

        # Injetar usuário logado no campo técnico se não foi enviado
        dados = request.data.copy()
        if not dados.get('tecnico') and request.user.is_authenticated:
            dados['tecnico'] = request.user.get_full_name() or request.user.username

        serializer = ElevConcluirOsSerializer(os_existente, data=dados, partial=True)
        serializer.is_valid(raise_exception=True)
        os_salva = serializer.save()

        # Lógica de Peças (Inteligente)
        houve_peca = dados.get('houve_substituicao_pecas')
        peca_desc = dados.get('peca_substituida')
        
        if houve_peca in ['Sim_Imediata', 'Sim_Posterior'] and peca_desc:
            from ..models.elev_so_model import PecaManutencao
            
            if houve_peca == 'Sim_Imediata':
                # Peça foi substituída
                PecaManutencao.objects.create(
                    elevador=os_salva.elevador,
                    tipo_peca=peca_desc,
                    ordem_servico=os_salva.protocolo,
                    tecnico_identificador=os_salva.tecnico,
                    tecnico=os_salva.tecnico,
                    status='SUBSTITUIDA',
                    data_efetiva_troca=os_salva.data_hora_conclusao.date() if os_salva.data_hora_conclusao else timezone.now().date(),
                    midia=os_salva.midia
                )
            elif houve_peca == 'Sim_Posterior':
                # Peça está pendente
                PecaManutencao.objects.create(
                    elevador=os_salva.elevador,
                    tipo_peca=peca_desc,
                    ordem_servico=os_salva.protocolo,
                    tecnico_identificador=os_salva.tecnico,
                    status='PENDENTE',
                    midia=os_salva.midia
                )

        from ..models.elev_so_model import ElevadorStatus
        try:
            elev_status = ElevadorStatus.objects.get(elevador=os_salva.elevador)
            
            if os_salva.elevador_parado == 'ATIVO':
                # Verifica se não há OUTRA OS aberta e parada
                outras_paradas = ElevOrderReg.objects.filter(elevador=os_salva.elevador, status='ABERTA', elevador_parado='PARADO').exists()
                if not outras_paradas:
                    # Registra o histórico da parada total se houver data de início
                    if elev_status.data_hora_parada:
                        from elevadores.serializers import calc_hrs_uteis_parado
                        from ..models.elev_so_model import ElevadorParadaHistorico
                        tmp_parado = calc_hrs_uteis_parado(elev_status.data_hora_parada, timezone.now())
                        hist = ElevadorParadaHistorico.objects.filter(elevador=os_salva.elevador, data_hora_retorno__isnull=True).first()
                        if hist:
                            hist.data_hora_retorno = timezone.now()
                            hist.tempo_parado = Decimal(str(tmp_parado))
                            hist.os_relacionada = os_salva
                            hist.save()
                        else:
                            ElevadorParadaHistorico.objects.create(
                                elevador=os_salva.elevador,
                                data_hora_parada=elev_status.data_hora_parada,
                                data_hora_retorno=timezone.now(),
                                tempo_parado=Decimal(str(tmp_parado)),
                                os_relacionada=os_salva
                            )
                    
                    elev_status.status = 'ATIVO'
                    elev_status.data_hora_parada = None
                    elev_status.save()
            elif os_salva.elevador_parado == 'PARADO':
                was_ativo = (elev_status.status != 'PARADO')
                elev_status.status = 'PARADO'
                
                # Se não tinha data_hora_parada anterior (estava ativo e ficou parado agora ou perdeu a data),
                # define como agora (ou data da OS)
                if not elev_status.data_hora_parada:
                    elev_status.data_hora_parada = os_salva.data_hora if os_salva.data_hora else timezone.now()
                
                elev_status.save()
                
                if was_ativo:
                    from ..models.elev_so_model import ElevadorParadaHistorico
                    hist_aberto = ElevadorParadaHistorico.objects.filter(elevador=os_salva.elevador, data_hora_retorno__isnull=True).exists()
                    if not hist_aberto:
                        ElevadorParadaHistorico.objects.create(
                            elevador=os_salva.elevador,
                            data_hora_parada=elev_status.data_hora_parada,
                            os_relacionada=os_salva
                        )
        except ElevadorStatus.DoesNotExist:
            pass

        if os_salva.status == 'CONCLUIDA':
            if houve_peca:
                self._disparar_notificacao(os_salva, 'os_elev_conclusao_peca', peca=peca_desc)
            else:
                self._disparar_notificacao(os_salva, 'os_elev_conclusao')
        elif os_salva.status == 'AGUARDANDO PEÇAS':
            self._disparar_notificacao(os_salva, 'os_elev_aguardando_peca', peca=peca_desc)

        return Response({
            'sucesso': True,
            'mensagem': f'Ordem de Serviço: {os_salva.protocolo}, salva com sucesso!'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='tecnicos_otis')
    def tecnicos_otis(self, request):
        empresas_ids = set()
        for c in Contratos.objects.all():
            if c.categoria and 'ELEVADORES' in [str(cat).upper() for cat in c.categoria]:
                if c.empresa_id:
                    empresas_ids.add(c.empresa_id)
        
        contatos = ContatoEmpresa.objects.filter(empresa_id__in=empresas_ids)
        tecnicos = []
        for contato in contatos:
            cargo = (contato.cargo or '').lower()
            if any(term in cargo for term in ['tecnico', 'tcnico', 'técnico', 't\u00e9cnico', 'tǸcnico']):
                tecnicos.append(contato.nome_contato)
        return Response(list(set(tecnicos)))

    @action(detail=False, methods=['get'], url_path='tecnicos_acompanhamento')
    def tecnicos_acompanhamento(self, request):
        tecnicos = User.objects.filter(groups__name__icontains='Elevadores')
        nomes = [t.get_full_name() or t.username for t in tecnicos]
        return Response(nomes)

    @action(detail=True, methods=['post'], url_path='registrar_chegada')
    def registrar_chegada(self, request, pk=None):
        os_existente = self.get_object()
        dados = request.data.copy()
        
        # Só permite registrar se ainda não estiver concluída
        if os_existente.status in ['CONCLUIDA', 'CONCLUÍDA']:
            return Response({'sucesso': False, 'mensagem': 'OS já está concluída.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Atualiza os dados
        tecnico = dados.get('tecnico', '')
        acompanhante = dados.get('acompanhante', '')
        registrador_chegada = dados.get('registrador_chegada', '')
        data_hora_chegada_raw = dados.get('data_hora_chegada')
        
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        if not data_hora_chegada_raw:
            data_hora_chegada = timezone.now()
        else:
            if isinstance(data_hora_chegada_raw, str):
                data_hora_chegada = parse_datetime(data_hora_chegada_raw)
                if timezone.is_naive(data_hora_chegada):
                    data_hora_chegada = timezone.make_aware(data_hora_chegada)
            else:
                data_hora_chegada = data_hora_chegada_raw

        os_existente.tecnico = tecnico
        os_existente.acompanhante = acompanhante
        os_existente.registrador_chegada = registrador_chegada
        os_existente.data_hora_chegada = data_hora_chegada
        os_existente.status = 'EM ANDAMENTO'
        os_existente.save()

        # Vincula novo técnico como contato da empresa se não existir
        if tecnico:
            # categoria é JSONField (lista), usar __contains para buscar dentro do array
            contrato = Contratos.objects.filter(categoria__contains='ELEVADORES').first()
            if contrato and contrato.empresa:
                otis = contrato.empresa
                contato_existe = otis.contatos.filter(nome_contato__iexact=tecnico.strip()).exists()
                if not contato_existe:
                    ContatoEmpresa.objects.create(
                        empresa=otis,
                        nome_contato=tecnico.strip(),
                        cargo='Técnico'
                    )

        # Dispara notificação de Andamento
        self._disparar_notificacao(os_existente, 'os_elev_andamento')

        return Response({
            'sucesso': True,
            'mensagem': 'Chegada do técnico registrada com sucesso.'
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
                'id': os.id,
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
                'midia': os.midia.url if os.midia else '',
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
        from ..models.elev_so_model import ElevadorStatus, ELEVATOR_CHOICE
        
        elevadores_parados = set(ElevadorStatus.objects.filter(status='PARADO').values_list('elevador', flat=True))

        qs_filtrado = ManutencaoPreventiva.objects.filter(
            mes_referencia__range=(kwargs['inicio'], kwargs['fim'])
        )
        
        elevadores_processados = {}
        
        for mpm in qs_filtrado:
            status = 'PARADO' if mpm.elevador in elevadores_parados else mpm.status
            data_exec = '' if status == 'PARADO' else (mpm.data_execucao.strftime('%d/%m/%Y') if mpm.data_execucao else '')
            elevadores_processados[mpm.elevador] = {
                'elevador': mpm.elevador,
                'data_execucao': data_exec,
                'ordem_servico': mpm.ordem_servico or '',
                'tecnico': mpm.tecnico or '',
                'status': status,
            }
            
        indicador_dois = []
        for key, name in ELEVATOR_CHOICE:
            if key in elevadores_processados:
                indicador_dois.append(elevadores_processados[key])
            else:
                status = 'PARADO' if key in elevadores_parados else 'PENDENTE'
                indicador_dois.append({
                    'elevador': key,
                    'data_execucao': '',
                    'ordem_servico': '',
                    'tecnico': '',
                    'status': status
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
        df['protocolo'] = df['protocolo'].fillna('-')
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
        # Disponibilidade Média Mensal (DMM) - Indicador 4
        from ..models.elev_so_model import ELEVATOR_CHOICE, ElevadorParadaHistorico
        from django.db.models import Sum
        from decimal import Decimal
        import datetime
        import holidays

        feriados_br = holidays.country_holidays('BR', language='pt_BR')
        HRS_UTEIS_DIA = 12.0

        inicio_dt = kwargs.get('inicio')
        fim_dt = kwargs.get('fim')

        inicio_date = inicio_dt.date() if hasattr(inicio_dt, 'date') else inicio_dt
        fim_date = fim_dt.date() if hasattr(fim_dt, 'date') else fim_dt

        qnt_dias_uteis = feriados_br.get_working_days_count(inicio_date, fim_date)
        qnt_horas_uteis_totais = Decimal(str(HRS_UTEIS_DIA * qnt_dias_uteis))

        # Inicializa todos os elevadores com 0 horas paradas
        dados_parada = {key: Decimal('0.0') for key, name in ELEVATOR_CHOICE}
        
        # Buscar todos os registros de paradas que de alguma forma tocam o intervalo [inicio, fim]
        # Uma parada afeta o ms atual se:
        # data_hora_parada <= fim AND (data_hora_retorno IS NULL OR data_hora_retorno >= inicio)
        # O banco de dados pode ter retornos nulos ou datas que ultrapassam o ms.
        
        from django.db.models import Q
        
        qs_hist = ElevadorParadaHistorico.objects.filter(
            Q(data_hora_parada__lte=fim_dt) & 
            (Q(data_hora_retorno__isnull=True) | Q(data_hora_retorno__gte=inicio_dt))
        )
        
        # Como o Django no calcula interseo nativamente em hrs teis, vamos somar o que a model calculou
        # OU calcular a interseco real. Para simplificar e manter a compatibilidade, vamos confiar que 'tempo_parado' 
        #  preenchido. Se a model `ElevadorParadaHistorico` j armazena o tempo_parado, ns s precisamos das paradas
        # que ocorreram neste ms. Se a data_hora_retorno est no ms, somamos o tempo_parado dela (se for parada longa, 
        # idealmente o tempo deve ser proporcional, mas a implementao atual agrupa por ms baseado no tempo total salvo).
        
        # Como o usurio pede: "se um elevador estiver parado a muito tempo, a disponibilidade ser 0"
        # Isso significa que se `data_hora_parada < inicio` e `data_hora_retorno`  nulo (ou > fim), o tempo parado no ms = `qnt_horas_uteis_totais`
        # Vamos tratar essa lgica iterando sobre o queryset:
        
        for p in qs_hist:
            elev_nome = p.elevador
            
            # Definir os limites de interseo para a parada no ms corrente
            parada_inicio = p.data_hora_parada.date()
            parada_fim = p.data_hora_retorno.date() if p.data_hora_retorno else fim_date
            
            # Interseção
            
            intersecao_inicio = max(inicio_date, parada_inicio)
            intersecao_fim = min(fim_date, parada_fim)
            
            if intersecao_inicio <= intersecao_fim:
                # Contar dias teis na interseo
                dias_uteis_parado = feriados_br.get_working_days_count(intersecao_inicio, intersecao_fim)
                hrs_paradas = Decimal(str(dias_uteis_parado * HRS_UTEIS_DIA))
                
                # Se for no mesmo dia e tiver tempo_parado armazenado, usa o tempo_parado para maior preciso
                if p.data_hora_parada.date() >= inicio_date and p.data_hora_retorno and p.data_hora_retorno.date() <= fim_date and p.tempo_parado:
                    hrs_paradas = p.tempo_parado
                elif hrs_paradas > qnt_horas_uteis_totais:
                    hrs_paradas = qnt_horas_uteis_totais
                    
                if elev_nome in dados_parada:
                    dados_parada[elev_nome] += hrs_paradas
        
        ind_quatro = []
        for elev_nome, total_parado in dados_parada.items():
            # No permitir horas negativas de disponibilidade
            if total_parado > qnt_horas_uteis_totais:
                total_parado = qnt_horas_uteis_totais
                
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

    def _disparar_notificacao(self, os, evento, peca=None):
        # Só dispara notificações para OS's do dia atual
        hoje = timezone.localtime(timezone.now()).date()
        if os.data_hora:
            data_os = timezone.localtime(os.data_hora).date()
            if data_os != hoje:
                return

        contato_queryset = Contato.objects.filter(is_ativo=True)
        if evento == 'os_elev_registro':
            template = TemplateMessage.objects.filter(tipo_evento=evento, is_ativo=True).first()
            if not template:
                return
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
        elif evento == 'os_elev_andamento':
            try:
                template = get_object_or_404(TemplateMessage, tipo_evento=evento, is_ativo=True)
                texto = template.base_text
            except:
                texto = "Olá {nome},\nO técnico {tecnico} chegou às {data_hora} para atender a OS {protocolo} do {elevador}.\nAcompanhante: {acompanhante}\nRegistrado por: {registrador_chegada}"

            for contato in contato_queryset:
                tel = contato.telefone
                text = texto.format(
                    nome=contato.nome,
                    tecnico=os.tecnico,
                    data_hora=os.data_hora_chegada.strftime("%d/%m/%Y às %H:%M") if os.data_hora_chegada else "",
                    protocolo=os.protocolo,
                    elevador=os.elevador,
                    acompanhante=os.acompanhante or "Não informado",
                    registrador_chegada=os.registrador_chegada or "Não informado"
                )
                try:
                    auto_message(tel, text)
                except Exception as e:
                    print(f"Erro na Evolution API: {e}")
        elif evento in ['os_elev_conclusao', 'os_elev_conclusao_peca', 'os_elev_aguardando_peca']:
            template = TemplateMessage.objects.filter(tipo_evento='os_elev_conclusao', is_ativo=True).first()
            if not template:
                return
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
                    
                    if evento == 'os_elev_conclusao_peca':
                        text += f"\n\n*Obs:* O equipamento voltou a operar, porém houve a necessidade de substituição/agendamento da peça: {peca}."
                    elif evento == 'os_elev_aguardando_peca':
                        text = f"Olá {contato.nome},\n\n*Aviso de Pendência:* O chamado (Protocolo: {os.protocolo}) referente ao {os.elevador} não pôde ser concluído. O elevador permanecerá PARADO aguardando a troca da peça: {peca}."
                    
                    auto_message(tel, text)   
                except Exception as e:
                    print(f"Erro na Evolution API: {e}")
        
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        
        serializer = DashboardFiltroSerializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)

        filtros = serializer.validated_data # type: ignore
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        import datetime
        hoje = timezone.now()
        if 'inicio' not in filtros:
            primeiro_dia_mes_atual = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filtros['inicio'] = primeiro_dia_mes_atual - relativedelta(months=1)
        if 'fim' not in filtros:
            # último dia do mês
            prox_mes = filtros['inicio'] + relativedelta(months=1)
            filtros['fim'] = prox_mes - datetime.timedelta(seconds=1)

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
                        
                        hist = ElevadorParadaHistorico.objects.filter(elevador=elevador_nome, data_hora_retorno__isnull=True).first()
                        if hist:
                            hist.data_hora_retorno = data_hora_retorno
                            hist.tempo_parado = Decimal(str(tmp_parado))
                            hist.save()
                        else:
                            ElevadorParadaHistorico.objects.create(
                                elevador=elevador_nome,
                                data_hora_parada=elev.data_hora_parada,
                                data_hora_retorno=data_hora_retorno,
                                tempo_parado=Decimal(str(tmp_parado))
                            )

                    elif novo_status == 'PARADO' and elev.status != 'PARADO':
                        if not elev.data_hora_parada:
                            elev.data_hora_parada = timezone.now()
                        
                        hist_aberto = ElevadorParadaHistorico.objects.filter(elevador=elevador_nome, data_hora_retorno__isnull=True).exists()
                        if not hist_aberto:
                            ElevadorParadaHistorico.objects.create(
                                elevador=elevador_nome,
                                data_hora_parada=elev.data_hora_parada
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

    @action(detail=False, methods=['get'], url_path='historico_mensal')
    def historico_mensal(self, request):
        mes_ano = request.query_params.get('mes')
        if not mes_ano:
            hoje = timezone.now()
            mes_ano = f"{hoje.year}-{hoje.month:02d}"
        
        try:
            ano, mes = map(int, mes_ano.split('-'))
        except ValueError:
            return Response({'error': 'Formato inválido. Use YYYY-MM'}, status=status.HTTP_400_BAD_REQUEST)
        
        from ..models import ELEVATOR_CHOICE
        elevadores_padrao = [choice[0] for choice in ELEVATOR_CHOICE]
        historico = {elev: [] for elev in elevadores_padrao}
        
        # 1. OS (ElevOrderReg)
        os_qs = ElevOrderReg.objects.filter(data_hora__year=ano, data_hora__month=mes)
        for os_obj in os_qs:
            if os_obj.elevador in historico:
                historico[os_obj.elevador].append({
                    'id': os_obj.id,
                    'tipo': 'OS',
                    'data_hora': os_obj.data_hora.isoformat() if os_obj.data_hora else None,
                    'badge': 'bg-primary',
                    'titulo': f"OS - {os_obj.tipo_chamado} ({os_obj.protocolo})",
                    'detalhes': f"Status: {os_obj.status} | Ocorrência: {os_obj.ocorrencia}",
                    'registrado_por': os_obj.atendente
                })
                
        # 2. Alarmes EMS (AlarmeEmsEvent)
        from ..models.elev_so_model import AlarmeEmsEvent
        alarme_qs = AlarmeEmsEvent.objects.filter(data_hora__year=ano, data_hora__month=mes)
        for alarme in alarme_qs:
            if alarme.elevador in historico:
                historico[alarme.elevador].append({
                    'tipo': 'ALARME',
                    'data_hora': alarme.data_hora.isoformat() if alarme.data_hora else None,
                    'badge': 'bg-danger' if alarme.tipo_evento == 'ALARM' else 'bg-warning text-dark',
                    'titulo': f"EMS - {alarme.tipo_evento}",
                    'detalhes': alarme.descricao,
                    'registrado_por': alarme.usuario_registrador
                })
                
        # 3. Manutenções Preventivas (MPM)
        from ..models import ManutencaoPreventiva
        mpm_qs = ManutencaoPreventiva.objects.filter(mes_referencia__year=ano, mes_referencia__month=mes)
        for mpm in mpm_qs:
            if mpm.elevador in historico:
                historico[mpm.elevador].append({
                    'tipo': 'MPM',
                    'data_hora': mpm.data_execucao.isoformat() if mpm.data_execucao else mpm.mes_referencia.isoformat(),
                    'badge': 'bg-success',
                    'titulo': "Manutenção Preventiva",
                    'detalhes': f"Mês Ref: {mpm.mes_referencia} | Status: {mpm.status}",
                    'registrado_por': mpm.tecnico
                })
                
        # 4. Peças (PecaManutencao)
        from ..models.elev_so_model import PecaManutencao
        pecas_qs = PecaManutencao.objects.filter(data_registro__year=ano, data_registro__month=mes)
        for peca in pecas_qs:
            if peca.elevador in historico:
                historico[peca.elevador].append({
                    'tipo': 'PEÇA',
                    'data_hora': peca.data_registro.isoformat() if peca.data_registro else None,
                    'badge': 'bg-info text-dark',
                    'titulo': f"Peça - {peca.tipo_peca}",
                    'detalhes': f"Status: {peca.status} | OS: {peca.ordem_servico}",
                    'registrado_por': peca.tecnico_identificador
                })
                
        resultado = []
        for elev, eventos in historico.items():
            eventos.sort(key=lambda x: x['data_hora'] or '', reverse=True)
            resultado.append({
                'elevador': elev,
                'eventos': eventos,
                'disponibilidade': 100,
                'tempo_parado_str': '--'
            })
            
        return Response(resultado, status=status.HTTP_200_OK)

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

class AlarmeEmsEventViewSet(viewsets.ModelViewSet):
    queryset = AlarmeEmsEvent.objects.all()
    serializer_class = AlarmeEmsEventSerializer

    def perform_create(self, serializer):
        user_name = self.request.user.get_full_name() or self.request.user.username if self.request.user.is_authenticated else 'Sistema'
        serializer.save(usuario_registrador=user_name)
        
       
        
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

from ..models.elev_so_model import ElevadorParadaHistorico
from ..serializers import ElevadorParadaHistoricoSerializer

class ElevadorParadaHistoricoViewSet(viewsets.ModelViewSet):
    queryset = ElevadorParadaHistorico.objects.all().order_by('-data_hora_parada')
    serializer_class = ElevadorParadaHistoricoSerializer
