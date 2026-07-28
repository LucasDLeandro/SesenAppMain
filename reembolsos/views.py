from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from django.db import transaction

from .models import ServidorReembolso, SolicitacaoReembolso, LimiteReembolso, ConfiguracaoRelatorio
from .serializers import ServidorReembolsoSerializer, SolicitacaoReembolsoSerializer, LimiteReembolsoSerializer, ConfiguracaoRelatorioSerializer

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER

@login_required
def dashboard_reembolsos(request):
    # Pode adicionar lógicas adicionais de contexto aqui, se necessário
    return render(request, 'reembolsos/dashboard.html')

class LimiteReembolsoViewSet(viewsets.ModelViewSet):
    queryset = LimiteReembolso.objects.all().order_by('indice')
    serializer_class = LimiteReembolsoSerializer

class ServidorReembolsoViewSet(viewsets.ModelViewSet):
    queryset = ServidorReembolso.objects.all().order_by('pessoa__nome')
    serializer_class = ServidorReembolsoSerializer

from .models import FaturaReembolso
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class ConfiguracaoRelatorioAPIView(APIView):
    def get(self, request):
        config, created = ConfiguracaoRelatorio.objects.get_or_create(id=1)
        serializer = ConfiguracaoRelatorioSerializer(config)
        return Response(serializer.data)

    def patch(self, request):
        config, created = ConfiguracaoRelatorio.objects.get_or_create(id=1)
        serializer = ConfiguracaoRelatorioSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SolicitacaoReembolsoViewSet(viewsets.ModelViewSet):
    queryset = SolicitacaoReembolso.objects.all().order_by('-criado_em')
    serializer_class = SolicitacaoReembolsoSerializer

    def _save_faturas(self, solicitacao, faturas_data):
        # Limpa as existentes e recria
        solicitacao.faturas.all().delete()
        for fd in faturas_data:
            # Converte valores de string (R$ 1.000,00) para float se vier string
            def parse_money(val):
                if not val: return None
                if isinstance(val, str):
                    val = val.replace('R$', '').replace('.', '').replace(',', '.').strip()
                from decimal import Decimal
                return Decimal(str(val)) if val else None

            FaturaReembolso.objects.create(
                solicitacao=solicitacao,
                periodo_inicio=fd.get('periodo_inicio') or None,
                periodo_fim=fd.get('periodo_fim') or None,
                valor_fatura=parse_money(fd.get('valor_fatura')),
                valor_servico=parse_money(fd.get('valor_servico')),
                fatura_anexa=fd.get('fatura_anexa'),
                comprovante_pagamento=fd.get('comprovante_pagamento'),
                aprovada=fd.get('aprovada', True),
                justificativa_negacao=fd.get('justificativa_negacao')
            )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        faturas_data = request.data.pop('faturas', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitacao = serializer.save()
        self._save_faturas(solicitacao, faturas_data)
        return Response(self.get_serializer(solicitacao).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        faturas_data = request.data.pop('faturas', [])
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        solicitacao = serializer.save()
        self._save_faturas(solicitacao, faturas_data)
        return Response(self.get_serializer(solicitacao).data)

from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
import datetime
from xhtml2pdf import pisa
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

@login_required
def gerar_pdf_controle_anual(request, pk):
    config, _ = ConfiguracaoRelatorio.objects.get_or_create(id=1)
    servidor = get_object_or_404(ServidorReembolso, pk=pk)
    ano_param = request.GET.get('ano')
    if ano_param and ano_param.isdigit():
        ano = int(ano_param)
    else:
        ano = datetime.date.today().year
    
    faturas = FaturaReembolso.objects.filter(
        solicitacao__servidor=servidor,
        periodo_inicio__year=ano
    ).order_by('periodo_inicio')
    
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    meses_data = []
    total_fatura = total_servico = total_max = total_res = 0
    
    obs_count = 1
    obs_paragraphs_data = []
    solicitacao_obs_map = {}
    
    for i in range(1, 13):
        s_mes = faturas.filter(periodo_inicio__month=i).first()
        teto_atual = servidor.cargo_limite.valor if servidor.cargo_limite else servidor.teto_ressarcimento
        
        if s_mes:
            periodo_str = f"{s_mes.periodo_inicio.strftime('%d/%m')} a {s_mes.periodo_fim.strftime('%d/%m/%Y')}"
            
            teto_aplicavel = teto_atual
            valor_servico_aplicavel = s_mes.valor_servico or 0
            data_portaria = servidor.data_publicacao_portaria
            if data_portaria and s_mes.periodo_inicio and s_mes.periodo_fim:
                if data_portaria > s_mes.periodo_fim:
                    teto_aplicavel = 0
                    valor_servico_aplicavel = 0
                elif s_mes.periodo_inicio < data_portaria <= s_mes.periodo_fim:
                    # d_pf = min(s_mes.periodo_fim.day, 30)
                    # d_dp = min(data_portaria.day, 30)
                    # dias_elegiveis = (s_mes.periodo_fim.year - data_portaria.year) * 360 + (s_mes.periodo_fim.month - data_portaria.month) * 30 + (d_pf - d_dp) + 1
                    dias_elegiveis = (s_mes.periodo_fim - data_portaria).days + 1
                    from decimal import Decimal, ROUND_DOWN
                    base_calculo = min(s_mes.valor_servico, teto_atual) if s_mes.valor_servico else 0
                    teto_aplicavel = ((base_calculo / Decimal(30)) * Decimal(dias_elegiveis)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    valor_servico_aplicavel = teto_aplicavel
            
            val_ressarcido_num = min(valor_servico_aplicavel, teto_aplicavel)
            # Garante que seja um número (0 se for None)
            valor_original_servico = s_mes.valor_servico or 0

            # O valor a exibir na coluna "A Serviço" será o menor entre o cobrado na fatura e o proporcional calculado
            valor_coluna_servico = min(valor_original_servico, valor_servico_aplicavel)
            
            val_fatura = f"R$ {s_mes.valor_fatura:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if s_mes.valor_fatura else "R$ 0,00"
            val_servico = f"R$ {valor_coluna_servico:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if s_mes.valor_servico else "R$ 0,00"
            val_max = f"R$ {teto_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            val_res = f"R$ {val_ressarcido_num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            total_fatura += s_mes.valor_fatura or 0
            total_servico += valor_coluna_servico
            total_max += teto_aplicavel or 0
            total_res += val_ressarcido_num or 0
            
            obs_col_text = "-"
            obs_parts = []
            
            # Solicitacao obs
            if s_mes.solicitacao and s_mes.solicitacao.observacoes:
                obs_parts_sol = [obs.strip() for obs in s_mes.solicitacao.observacoes.split('|||') if obs.strip()]
                for idx, obs_text in enumerate(obs_parts_sol):
                    sol_id = f"{s_mes.solicitacao.id}_obs_{idx}"
                    if sol_id not in solicitacao_obs_map:
                        obs_label = f"Obs {obs_count}"
                        solicitacao_obs_map[sol_id] = obs_label
                        obs_paragraphs_data.append(f"<b>{obs_label}:</b> {obs_text}")
                        obs_count += 1
                    obs_parts.append(solicitacao_obs_map[sol_id])
                
            # Fatura negada obs
            if not getattr(s_mes, 'aprovada', True):
                just = s_mes.justificativa_negacao or 'Fatura negada.'
                obs_label = f"Obs {obs_count}"
                obs_paragraphs_data.append(f"<b>{obs_label}:</b> [Fatura Negada]: {just}")
                obs_count += 1
                obs_parts.append(obs_label)
                
            if obs_parts:
                obs_col_text = ", ".join(obs_parts)
            
            meses_data.append([periodo_str, val_fatura, val_servico, val_max, val_res, obs_col_text])
        else:
            val_max = f"R$ {teto_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            total_max += teto_atual or 0
            meses_data.append(['-', 'R$ 0,00', 'R$ 0,00', val_max, 'R$ -', '-'])

    tot_fatura_str = f"R$ {total_fatura:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    tot_serv_str = f"R$ {total_servico:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    tot_max_str = f"R$ {total_max:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    tot_res_str = f"R$ {total_res:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    meses = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 
             7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
    mes_str = ""
    ano_str = str(ano)
    if faturas.exists():
        ultima_fatura = faturas.order_by('-periodo_inicio').first()
        if ultima_fatura and ultima_fatura.periodo_inicio:
            mes_str = meses.get(ultima_fatura.periodo_inicio.month, "")
            ano_str = str(ultima_fatura.periodo_inicio.year)
    else:
        mes_str = meses.get(datetime.date.today().month, "")
        
    if mes_str:
        filename = f"{servidor.nome} - {mes_str} de {ano_str}.pdf"
    else:
        filename = f"{servidor.nome} - {ano_str}.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    doc = SimpleDocTemplate(
        response, 
        pagesize=A4, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30,
        title=filename.replace('.pdf', '')
    )
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)
    subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.lightblue)
    right_title_style = ParagraphStyle('RightTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.white, alignment=TA_RIGHT)
    right_sub_style = ParagraphStyle('RightSub', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.lightblue, alignment=TA_RIGHT)
    
    header_data = [
        [
            Paragraph(f"{config.cabecalho_linha1}<br/>{config.cabecalho_linha2}<br/>{config.cabecalho_linha3}", subtitle_style),
            Paragraph(f"RELATÓRIO DE REEMBOLSO<br/>Ano Base: {ano}<br/>Emissão: {datetime.date.today().strftime('%d/%m/%Y')}", right_sub_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[280, 250])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e3c72')),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 15))
    
    cargo_str = servidor.cargo_limite.cargo if servidor.cargo_limite else servidor.cargo
    info_data1 = [
        ['NOME:', servidor.nome.upper()],
        ['CARGO:', cargo_str]
    ]
    if servidor.protocolo_autorizacao:
        info_data1.append(['AUTORIZAÇÃO:', servidor.protocolo_autorizacao])
    t_info1 = Table(info_data1, colWidths=[80, 450])
    t_info1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_info1)
    elements.append(Spacer(1, 10))
    
    def format_cpf_br(cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf

    def format_telefone_br(tel):
        tel = ''.join(filter(str.isdigit, str(tel)))
        if len(tel) == 13 and tel.startswith('55'):
            return f"+55 ({tel[2:4]}) {tel[4]} {tel[5:9]}-{tel[9:]}"
        elif len(tel) == 12 and tel.startswith('55'):
            return f"+55 ({tel[2:4]}) {tel[4:8]}-{tel[8:]}"
        elif len(tel) == 11:
            return f"({tel[:2]}) {tel[2]} {tel[3:7]}-{tel[7:]}"
        elif len(tel) == 10:
            return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        return tel

    banco_title = [['DADOS BANCÁRIOS', '', '', '']]
    banco_header = [['CPF', 'Banco', 'Agência', 'Conta Corrente']]
    banco_data = [[format_cpf_br(servidor.cpf), servidor.banco, servidor.agencia, servidor.conta_corrente]]
    
    t_banco = Table(banco_title + banco_header + banco_data, colWidths=[132.5, 132.5, 132.5, 132.5])
    t_banco.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (3,0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,1), (3,1), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_banco)
    elements.append(Spacer(1, 10))
    
    tel_data = [
        ['Telefone:', format_telefone_br(servidor.telefone_linha), 'Ressarcimento de Telefonia']
    ]
    t_tel = Table(tel_data, colWidths=[80, 150, 300])
    t_tel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (2,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_tel)
    elements.append(Spacer(1, 15))
    
    title_box = Table([[config.titulo_tabela_anual]], colWidths=[530])
    title_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0,0), (0,0), colors.HexColor('#1565c0')),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#90caf9')),
        ('PADDING', (0,0), (0,0), 6),
    ]))
    elements.append(title_box)
    elements.append(Spacer(1, 10))
    
    main_header = [['Período', 'Valor Total da Fatura', 'Valor Utilizado a Serviço', 'Limite Mensal', 'Valor a Ressarcir', 'Observações']]
    main_tot = [['TOTAIS', tot_fatura_str, tot_serv_str, tot_max_str, tot_res_str, '']]
    
    obs_style = ParagraphStyle('ObsStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=TA_CENTER)
    
    formatted_meses = []
    for m in meses_data:
        m_copy = list(m)
        m_copy[5] = Paragraph(m_copy[5], obs_style)
        formatted_meses.append(m_copy)
        
    t_main = Table(main_header + formatted_meses + main_tot, colWidths=[85, 85, 105, 80, 75, 100])
    t_main_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 4),
        
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#1565c0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor('#1e3c72')),
    ])
    
    for i in range(1, 13):
        if meses_data[i-1][1] != 'R$ 0,00':
            t_main_style.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#2e7d32'))
            t_main_style.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')

    t_main.setStyle(t_main_style)
    elements.append(t_main)
    elements.append(Spacer(1, 15))
    
    note1 = Paragraph(config.nota_rodape_1, styles['Normal'])
    elements.append(note1)
    elements.append(Spacer(1, 10))
    
    if servidor.nota_designacao:
        note2 = Paragraph(f"{config.nota_rodape_2_prefix} {servidor.nota_designacao}", styles['Normal'])
    else:
        note2 = Paragraph(f"{config.nota_rodape_2_prefix} O(a) Servidor(a) {servidor.nome} foi nomeado(a) para exercer o cargo em comissão de {cargo_str}, conforme {servidor.portaria_designacao}.", styles['Normal'])
    elements.append(note2)
    elements.append(Spacer(1, 10))
    
    if servidor.nota_autorizacao:
        note3 = Paragraph(f"<b>Nota de Autorização:</b> {servidor.nota_autorizacao}", styles['Normal'])
        elements.append(note3)
        elements.append(Spacer(1, 10))
    
    if servidor.observacoes:
        obs_label = f"Obs {obs_count}"
        obs_paragraphs_data.append(f"<b>{obs_label}:</b> {servidor.observacoes}")
    
    for obs_text in obs_paragraphs_data:
        elements.append(Paragraph(obs_text, styles['Normal']))
        elements.append(Spacer(1, 5))
    
    doc.build(elements)
    return response

@login_required
def gerar_pdf_solicitacao(request, pk):
    config, _ = ConfiguracaoRelatorio.objects.get_or_create(id=1)
    from django.db.models import Q
    solicitacao = get_object_or_404(SolicitacaoReembolso, pk=pk)
    servidor = solicitacao.servidor
    
    faturas_solicitacao = solicitacao.faturas.all().order_by('periodo_inicio')
    
    ano_param = request.GET.get('ano')
    if ano_param:
        try:
            ano = int(ano_param)
        except ValueError:
            ano = datetime.date.today().year
    else:
        if faturas_solicitacao.exists() and faturas_solicitacao.first().periodo_inicio:
            ano = faturas_solicitacao.first().periodo_inicio.year
        else:
            ano = datetime.date.today().year

    faturas_ano = FaturaReembolso.objects.filter(
        solicitacao__servidor=servidor,
        periodo_inicio__year=ano
    ).order_by('periodo_inicio')
    
    obs_count = 1
    obs_paragraphs_data = []
    obs_col_solicitacao = []
    obs_col_servidor = None
    
    if solicitacao.observacoes:
        obs_parts_sol = [obs.strip() for obs in solicitacao.observacoes.split('|||') if obs.strip()]
        for obs_text in obs_parts_sol:
            obs_label = f"Obs {obs_count}"
            obs_paragraphs_data.append(f"<b>{obs_label}:</b> {obs_text}")
            obs_col_solicitacao.append(obs_label)
            obs_count += 1
        
    if servidor.observacoes:
        obs_col_servidor = f"Obs {obs_count}"
        obs_paragraphs_data.append(f"<b>Obs {obs_count}:</b> {servidor.observacoes}")
        obs_count += 1
        
    meses_data = []
    total_fatura = total_servico = total_max = total_res = 0
    highlighted_rows = []
    
    for i in range(1, 13):
        s_mes = faturas_ano.filter(periodo_inicio__month=i).first()
        teto_atual = servidor.cargo_limite.valor if servidor.cargo_limite else servidor.teto_ressarcimento
        
        if s_mes:
            periodo_str = f"{s_mes.periodo_inicio.strftime('%d/%m')} a {s_mes.periodo_fim.strftime('%d/%m/%Y')}"
            
            teto_aplicavel = teto_atual
            valor_servico_aplicavel = s_mes.valor_servico or 0
            data_portaria = servidor.data_publicacao_portaria
            if data_portaria and s_mes.periodo_inicio and s_mes.periodo_fim:
                if data_portaria > s_mes.periodo_fim:
                    teto_aplicavel = 0
                    valor_servico_aplicavel = 0
                elif s_mes.periodo_inicio < data_portaria <= s_mes.periodo_fim:
                    # d_pf = min(s_mes.periodo_fim.day, 30)
                    # d_dp = min(data_portaria.day, 30)
                    # dias_elegiveis = (s_mes.periodo_fim.year - data_portaria.year) * 360 + (s_mes.periodo_fim.month - data_portaria.month) * 30 + (d_pf - d_dp) + 1
                    dias_elegiveis = (s_mes.periodo_fim - data_portaria).days + 1
                    from decimal import Decimal, ROUND_DOWN
                    base_calculo = min(s_mes.valor_servico, teto_atual) if s_mes.valor_servico else 0
                    teto_aplicavel = ((base_calculo / Decimal(30)) * Decimal(dias_elegiveis)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                    valor_servico_aplicavel = teto_aplicavel
            
            val_ressarcido_num = min(valor_servico_aplicavel, teto_aplicavel)
            # Garante que seja um número (0 se for None)
            valor_original_servico = s_mes.valor_servico or 0

            # O valor a exibir na coluna "A Serviço" será o menor entre o cobrado na fatura e o proporcional calculado
            valor_coluna_servico = min(valor_original_servico, valor_servico_aplicavel)

            val_fatura = f"R$ {s_mes.valor_fatura:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if s_mes.valor_fatura else "R$ 0,00"
            val_servico = f"R$ {valor_coluna_servico:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if s_mes.valor_servico else "R$ 0,00"
            val_max = f"R$ {teto_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            val_res = f"R$ {val_ressarcido_num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            total_fatura += s_mes.valor_fatura or 0
            total_servico += valor_coluna_servico
            total_max += teto_aplicavel or 0
            total_res += val_ressarcido_num or 0
            
            obs_texts = []
            if s_mes in faturas_solicitacao and obs_col_solicitacao:
                obs_texts.extend(obs_col_solicitacao)
            if obs_col_servidor:
                obs_texts.append(obs_col_servidor)
                
            # Fatura negada obs
            if not getattr(s_mes, 'aprovada', True):
                just = s_mes.justificativa_negacao or 'Fatura negada.'
                obs_label = f"Obs {obs_count}"
                obs_paragraphs_data.append(f"<b>{obs_label}:</b> [Fatura Negada]: {just}")
                obs_count += 1
                obs_texts.append(obs_label)
                
            obs_col_text = ", ".join(obs_texts) if obs_texts else "-"
            
            meses_data.append([periodo_str, val_fatura, val_servico, val_max, val_res, obs_col_text])
            
            if s_mes in faturas_solicitacao:
                highlighted_rows.append(i)
        else:
            val_max = f"R$ {teto_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            total_max += teto_atual or 0
            meses_data.append(['-', 'R$ 0,00', 'R$ 0,00', val_max, 'R$ -', '-'])

    tot_fatura_str = f"R$ {total_fatura:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    tot_serv_str = f"R$ {total_servico:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    tot_max_str = f"R$ {total_max:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    tot_res_str = f"R$ {total_res:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    meses = {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN', 
             7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
    mes_str = ""
    ano_str = str(ano)
    if faturas_solicitacao.exists():
        ultima_fatura = faturas_solicitacao.order_by('-periodo_inicio').first()
        if ultima_fatura and ultima_fatura.periodo_inicio:
            mes_str = meses.get(ultima_fatura.periodo_inicio.month, "")
            ano_str = str(ultima_fatura.periodo_inicio.year)
    else:
        mes_str = meses.get(datetime.date.today().month, "")
        
    if mes_str:
        filename = f"{servidor.nome} - {mes_str} de {ano_str}.pdf"
    else:
        filename = f"{servidor.nome} - {ano_str}.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    doc = SimpleDocTemplate(
        response, 
        pagesize=A4, 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=30, 
        bottomMargin=30,
        title=filename.replace('.pdf', '')
    )
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.white)
    subtitle_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.lightblue)
    right_title_style = ParagraphStyle('RightTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.white, alignment=TA_RIGHT)
    right_sub_style = ParagraphStyle('RightSub', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.lightblue, alignment=TA_RIGHT)
    
    header_data = [
        [
            Paragraph(f"{config.cabecalho_linha1}<br/>{config.cabecalho_linha2}<br/>{config.cabecalho_linha3}", subtitle_style),
            Paragraph(f"SOLICITAÇÃO DE REEMBOLSO<br/>Protocolo SEI: {solicitacao.protocolo_sei or '-'}<br/>Emissão: {datetime.date.today().strftime('%d/%m/%Y')}", right_sub_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[280, 250])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e3c72')),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 15))
    
    cargo_str = servidor.cargo_limite.cargo if servidor.cargo_limite else servidor.cargo
    info_data1 = [
        ['NOME:', servidor.nome.upper()],
        ['CARGO:', cargo_str]
    ]
    if servidor.protocolo_autorizacao:
        info_data1.append(['AUTORIZAÇÃO:', servidor.protocolo_autorizacao])
    t_info1 = Table(info_data1, colWidths=[80, 450])
    t_info1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_info1)
    elements.append(Spacer(1, 10))
    
    def format_cpf_br(cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else cpf

    def format_telefone_br(tel):
        tel = ''.join(filter(str.isdigit, str(tel)))
        if len(tel) == 13 and tel.startswith('55'):
            return f"+55 ({tel[2:4]}) {tel[4]} {tel[5:9]}-{tel[9:]}"
        elif len(tel) == 12 and tel.startswith('55'):
            return f"+55 ({tel[2:4]}) {tel[4:8]}-{tel[8:]}"
        elif len(tel) == 11:
            return f"({tel[:2]}) {tel[2]} {tel[3:7]}-{tel[7:]}"
        elif len(tel) == 10:
            return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
        return tel

    banco_title = [['DADOS BANCÁRIOS', '', '', '']]
    banco_header = [['CPF', 'Banco', 'Agência', 'Conta Corrente']]
    banco_data = [[format_cpf_br(servidor.cpf), servidor.banco, servidor.agencia, servidor.conta_corrente]]
    
    t_banco = Table(banco_title + banco_header + banco_data, colWidths=[132.5, 132.5, 132.5, 132.5])
    t_banco.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (3,0), colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,1), (3,1), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_banco)
    elements.append(Spacer(1, 10))
    
    tel_data = [
        ['Telefone:', format_telefone_br(servidor.telefone_linha), 'Ressarcimento de Telefonia']
    ]
    t_tel = Table(tel_data, colWidths=[80, 150, 300])
    t_tel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (2,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_tel)
    elements.append(Spacer(1, 15))
    
    title_box = Table([[config.titulo_tabela_anual]], colWidths=[530])
    title_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0,0), (0,0), colors.HexColor('#1565c0')),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('BOX', (0,0), (0,0), 1, colors.HexColor('#90caf9')),
        ('PADDING', (0,0), (0,0), 6),
    ]))
    elements.append(title_box)
    elements.append(Spacer(1, 10))
    
    main_header = [['Período', 'Valor Total da Fatura', 'Valor Utilizado a Serviço', 'Limite Mensal', 'Valor a Ressarcir', 'Observações']]
    main_tot = [['TOTAIS', tot_fatura_str, tot_serv_str, tot_max_str, tot_res_str, '']]
    
    obs_style = ParagraphStyle('ObsStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=TA_CENTER)
    
    formatted_meses = []
    for m in meses_data:
        m_copy = list(m)
        m_copy[5] = Paragraph(m_copy[5], obs_style)
        formatted_meses.append(m_copy)
        
    t_main = Table(main_header + formatted_meses + main_tot, colWidths=[85, 85, 105, 80, 75, 100])
    t_main_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3c72')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0,0), (-1,-1), 4),
        
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#1565c0')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor('#1e3c72')),
    ])
    
    for row_idx in highlighted_rows:
        t_main_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#dcfce7'))
        t_main_style.add('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold')

    for i in range(1, 13):
        if meses_data[i-1][1] != 'R$ 0,00':
            t_main_style.add('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#2e7d32'))
            if i not in highlighted_rows:
                t_main_style.add('FONTNAME', (4, i), (4, i), 'Helvetica-Bold')

    t_main.setStyle(t_main_style)
    elements.append(t_main)
    elements.append(Spacer(1, 15))
    
    note1 = Paragraph(config.nota_rodape_1, styles['Normal'])
    elements.append(note1)
    elements.append(Spacer(1, 10))
    
    if servidor.nota_designacao:
        note2 = Paragraph(f"{config.nota_rodape_2_prefix} {servidor.nota_designacao}", styles['Normal'])
    else:
        note2 = Paragraph(f"{config.nota_rodape_2_prefix} O(a) Servidor(a) {servidor.nome} foi nomeado(a) para exercer o cargo em comissão de {cargo_str}, conforme {servidor.portaria_designacao}.", styles['Normal'])
    elements.append(note2)
    elements.append(Spacer(1, 10))
    
    if servidor.nota_autorizacao:
        note3 = Paragraph(f"<b>Autorização:</b> {servidor.nota_autorizacao}", styles['Normal'])
        elements.append(note3)
        elements.append(Spacer(1, 10))
    
    for obs_text in obs_paragraphs_data:
        elements.append(Paragraph(obs_text, styles['Normal']))
        elements.append(Spacer(1, 5))
    
    doc.build(elements)
    return response