from django.db import models

class LimiteReembolso(models.Model):
    indice = models.IntegerField(unique=True)
    cargo = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    requer_autorizacao = models.BooleanField(default=False, help_text="Se marcado, exibirá os campos de autorização no formulário.")

    def __str__(self):
        return f"{self.indice} - {self.cargo} (R$ {self.valor})"

class ServidorReembolso(models.Model):
    pessoa = models.ForeignKey('usuarios.Pessoa', on_delete=models.CASCADE, null=True, blank=True, related_name="servidores_reembolso")
    
    @property
    def nome(self):
        return self.pessoa.nome if self.pessoa else ''

    @property
    def cpf(self):
        return self.pessoa.cpf if self.pessoa else ''


    cargo_limite = models.ForeignKey(
        LimiteReembolso,
        on_delete=models.PROTECT,
        null=True,
        related_name='servidores'
    )
    
    cargo = models.CharField(max_length=150, help_text="Ex: Assessor-Chefe, CJ-3", blank=True, null=True)
    portaria_designacao = models.CharField(max_length=200, blank=True, null=True, help_text="Ex: Portaria 380, de 28 de agosto de 2025")
    data_publicacao_portaria = models.DateField(blank=True, null=True, help_text="Data de publicação da portaria")
    protocolo_autorizacao = models.CharField(max_length=50, blank=True, null=True, help_text="Protocolo SEI de autorização, caso exigido")
    inicio_validade_autorizacao = models.DateField(blank=True, null=True, help_text="Data de início da validade da autorização")
    
    # Dados Bancários
    banco = models.CharField(max_length=100, help_text="Ex: Banco do Brasil")
    agencia = models.CharField(max_length=50)
    conta_corrente = models.CharField(max_length=50)
    
    # Contato e Configurações
    telefone_linha = models.CharField(max_length=20, help_text="Linha Telefônica Utilizada (ex: 61 99943-9030)")
    teto_ressarcimento = models.DecimalField(max_digits=10, decimal_places=2, default=330.00, help_text="Valor máximo de ressarcimento mensal (Art. 1º IN 10/2014)")

    # Campos Adicionais para PDF
    nota_designacao = models.TextField(blank=True, null=True, help_text="Texto completo da Nota de Designação para o PDF")
    nota_autorizacao = models.TextField(blank=True, null=True, help_text="Texto completo da Nota de Autorização para o PDF")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações adicionais para o PDF")

    ativo = models.BooleanField(default=True, help_text="Indica se o servidor está ativo para receber reembolsos")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

class StatusSolicitacaoReembolso(models.TextChoices):
    EM_ANALISE = 'em_analise', 'Em Análise'
    PENDENTE = 'pendente', 'Pendente'
    ENVIADO = 'enviado', 'Enviado'
    APROVADA = 'aprovada', 'Aprovada'
    CONCLUIDO = 'concluido', 'Concluído'
    NEGADA = 'negada', 'Negada'

class SolicitacaoReembolso(models.Model):
    servidor = models.ForeignKey(ServidorReembolso, on_delete=models.CASCADE, related_name="solicitacoes")
    
    # Anexos e Infos Gerais
    protocolo_sei = models.CharField(max_length=50, blank=True, null=True, help_text="Protocolo SEI da Solicitação")
    
    # Pagamento Posterior
    protocolo_ordem_bancaria = models.CharField(max_length=100, blank=True, null=True, help_text="Protocolo SEI da Ordem Bancária de Pagamento")
    data_pagamento = models.DateField(blank=True, null=True, help_text="Data do Pagamento")
    
    observacoes = models.TextField(blank=True, null=True, help_text="Informações Complementares")
    
    status = models.CharField(
        max_length=20,
        choices=StatusSolicitacaoReembolso.choices,
        default=StatusSolicitacaoReembolso.EM_ANALISE
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def valor_ressarcido(self):
        return sum(f.valor_ressarcido for f in self.faturas.all() if f.valor_ressarcido)
        
    @property
    def periodo_inicio(self):
        faturas = self.faturas.order_by('periodo_inicio')
        if faturas.exists() and faturas.first().periodo_inicio:
            return faturas.first().periodo_inicio
        return None

    @property
    def periodo_fim(self):
        faturas = self.faturas.order_by('-periodo_fim')
        if faturas.exists() and faturas.first().periodo_fim:
            return faturas.first().periodo_fim
        return None

    def __str__(self):
        return f"Solicitação {self.id} - {self.servidor.nome}"

class FaturaReembolso(models.Model):
    solicitacao = models.ForeignKey(SolicitacaoReembolso, on_delete=models.CASCADE, related_name="faturas")
    
    # Período da Despesa
    periodo_inicio = models.DateField(blank=True, null=True, help_text="Data de início do período da fatura")
    periodo_fim = models.DateField(blank=True, null=True, help_text="Data de fim do período da fatura")
    
    # Valores
    valor_fatura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor Total da Fatura")
    valor_servico = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor Utilizado a Serviço")
    valor_ressarcido = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor a ser Ressarcido (Calculado)")
    
    # Anexos
    fatura_anexa = models.CharField(max_length=200, blank=True, null=True, help_text="Número SEI da Fatura ou link")
    comprovante_pagamento = models.CharField(max_length=200, blank=True, null=True, help_text="Número SEI do Comprovante")

    # Aprovação e Negação
    aprovada = models.BooleanField(default=True, help_text="Indica se esta fatura específica foi aprovada")
    justificativa_negacao = models.TextField(blank=True, null=True, help_text="Justificativa caso a fatura seja negada")

    def save(self, *args, **kwargs):
        # Se a fatura não foi aprovada, o valor ressarcido é 0
        if not self.aprovada:
            self.valor_ressarcido = 0
            super().save(*args, **kwargs)
            return

        # Calcula o valor ressarcido por fatura (Mínimo entre o valor do serviço e o teto do servidor)
        if self.valor_servico is not None and self.solicitacao and self.solicitacao.servidor:
            teto_mensal = self.solicitacao.servidor.cargo_limite.valor if self.solicitacao.servidor.cargo_limite else self.solicitacao.servidor.teto_ressarcimento
            
            teto_aplicavel = teto_mensal
            
            # Se o servidor tem uma autorização com início, ela substitui a data da portaria para efeitos de cálculo.
            data_base_calculo = self.solicitacao.servidor.inicio_validade_autorizacao or self.solicitacao.servidor.data_publicacao_portaria
            
            valor_servico_aplicavel = self.valor_servico
            if data_base_calculo and self.periodo_inicio and self.periodo_fim:
                import datetime
                
                def parse_to_date(val):
                    if isinstance(val, str):
                        try:
                            return datetime.datetime.strptime(val, "%Y-%m-%d").date()
                        except ValueError:
                            return None
                    return val

                dp = parse_to_date(data_base_calculo)
                pi = parse_to_date(self.periodo_inicio)
                pf = parse_to_date(self.periodo_fim)

                if dp and pi and pf:
                    if dp > pf:
                        teto_aplicavel = 0
                        valor_servico_aplicavel = 0
                    elif pi < dp <= pf:
                        # d_pf = min(pf.day, 30)
                        # d_dp = min(dp.day, 30)
                        # dias_elegiveis = (pf.year - dp.year) * 360 + (pf.month - dp.month) * 30 + (d_pf - d_dp) + 1
                        dias_elegiveis = (pf - dp).days + 1
                        from decimal import Decimal, ROUND_DOWN
                        teto_aplicavel = ((teto_mensal / Decimal(30)) * Decimal(dias_elegiveis)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
                        valor_servico_aplicavel = ((self.valor_servico / Decimal(30)) * Decimal(dias_elegiveis)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
            
            if valor_servico_aplicavel > teto_aplicavel:
                self.valor_ressarcido = teto_aplicavel
            else:
                self.valor_ressarcido = valor_servico_aplicavel
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Fatura {self.id} da Solicitação {self.solicitacao_id}"

class ConfiguracaoRelatorio(models.Model):
    cabecalho_linha1 = models.CharField(max_length=200, default="Tribunal Superior Eleitoral", help_text="Primeira linha do cabeçalho")
    cabecalho_linha2 = models.CharField(max_length=200, default="Secretaria de Administração", help_text="Segunda linha do cabeçalho")
    cabecalho_linha3 = models.CharField(max_length=200, default="Seção de Equipamentos e Sistemas de Engenharia", help_text="Terceira linha do cabeçalho")
    
    titulo_tabela_anual = models.CharField(max_length=255, default="CONTROLE DOS VALORES GASTOS ANUALMENTE COM TELEFONIA MÓVEL - Nº 11 DE 2022", help_text="Título exibido acima da tabela principal")
    
    nota_rodape_1 = models.TextField(default="<b>(*)</b> Para fins de apuração do período em que se deu os gastos com telefonia móvel, utilizar-se-á o Regime de Competência. Este Regime tem os valores contabilizados dentro do mês onde se iniciou o fato Gerador.<br/><br/><b>(**)</b> Na Instrução Normativa TSE nº 11/2022 - Anexo I está a tabela referencial de valores máximos a serem custeados pelo Tribunal.", help_text="Texto da primeira nota de rodapé")
    
    nota_rodape_2_prefix = models.CharField(max_length=100, default="<b>Nota de Designação:</b>", help_text="Prefixo da nota de designação")
    
    def save(self, *args, **kwargs):
        # Garante que seja um singleton (apenas 1 registro)
        if self._state.adding and ConfiguracaoRelatorio.objects.exists():
            raise ValueError('Já existe uma configuração registrada.')
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configurações do Relatório de Reembolso"

