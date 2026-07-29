from django.db import models
from decimal import Decimal
from empresas.models import Empresa
from django.contrib.auth.models import User

class ProcessoLicitatorio(models.Model):
    FASES = [
        ('PREVISTA', 'Prevista'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('FINALIZADA', 'Finalizada'),
        ('SUSPENSA', 'Suspensa'),
        ('PLANEJAMENTO', 'Planejamento'),
        ('SELECAO', 'Seleção de Fornecedor'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado')
    ]
    PRIORIDADES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente')
    ]
    numero_processo = models.CharField(max_length=50, unique=True)
    objeto = models.TextField(blank=True, null=True)
    descricao_objeto = models.TextField(blank=True, null=True)
    justificativa = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADES, default='MEDIA')
    
    unidade_responsavel = models.CharField(max_length=150, blank=True, null=True)
    fase = models.CharField(max_length=20, choices=FASES, default='PREVISTA')
    valor_previsto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    esta_no_pac = models.BooleanField(default=False)
    eleicoes_ano_corrente = models.BooleanField(default=False)
    servidor_responsavel = models.CharField(max_length=150, blank=True, null=True)
    data_prevista_conclusao = models.DateField(blank=True, null=True)
    
    modalidade = models.CharField(max_length=50, blank=True, null=True)
    oficializacao_demanda_data = models.DateField(blank=True, null=True)
    
    status_etp = models.CharField(max_length=30, blank=True, null=True)
    link_etp = models.CharField(max_length=255, blank=True, null=True)
    
    status_tr = models.CharField(max_length=30, blank=True, null=True)
    link_tr = models.CharField(max_length=255, blank=True, null=True)
    
    status_edital = models.CharField(max_length=30, blank=True, null=True)
    link_edital = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def status_cronograma(self):
        from datetime import date
        cronogramas = self.cronogramas.all()
        if not cronogramas.exists():
            return "Sem Cronograma"
        
        # Verifica se alguma fase pendente tem prazo vencido
        atrasados = [c for c in cronogramas if not c.data_entrega_real and c.prazo_entrega < date.today()]
        if atrasados:
            return "Atrasado"
        
        return "No Prazo"

    def __str__(self):
        return f"{self.numero_processo} - {self.get_fase_display()}"

class TramitacaoSEI(models.Model):
    contratacao = models.ForeignKey(ProcessoLicitatorio, on_delete=models.CASCADE, related_name="tramitacoes")
    unidade_atual = models.CharField(max_length=150)
    data_entrada = models.DateField()
    data_saida = models.DateField(blank=True, null=True)
    prazo_retorno = models.DateField(blank=True, null=True)
    unidade_ultima_assinatura = models.CharField(max_length=150, blank=True, null=True)
    
    # Novos campos
    data_ultima_movimentacao = models.DateField(blank=True, null=True)
    motivo = models.TextField(blank=True, null=True)
    atribuido_a = models.CharField(max_length=150, blank=True, null=True)
    depende_de_nos = models.BooleanField(default=False)
    
    atualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tramitacoes_atualizadas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def tempo_na_unidade(self):
        from datetime import date
        end_date = self.data_saida if self.data_saida else date.today()
        return (end_date - self.data_entrada).days

    @property
    def dentro_do_cronograma(self):
        if not self.prazo_retorno:
            return True
        from datetime import date
        end_date = self.data_saida if self.data_saida else date.today()
        return end_date <= self.prazo_retorno

    def __str__(self):
        return f"{self.unidade_atual} - {self.contratacao.numero_processo}"

class CronogramaContratacao(models.Model):
    FASES_ARTEFATO = [
        ('ETP', 'Estudo Técnico Preliminar (ETP)'),
        ('TR', 'Termo de Referência (TR)'),
        ('PESQUISA', 'Pesquisa de Preços'),
        ('EDITAL', 'Edital'),
        ('JURIDICO', 'Parecer Jurídico'),
        ('OUTRO', 'Outro')
    ]
    contratacao = models.ForeignKey(ProcessoLicitatorio, on_delete=models.CASCADE, related_name="cronogramas")
    fase_artefato = models.CharField(max_length=20, choices=FASES_ARTEFATO)
    prazo_entrega = models.DateField()
    data_entrega_real = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status(self):
        from datetime import date
        if self.data_entrega_real:
            return "Entregue"
        if self.prazo_entrega < date.today():
            return "Atrasado"
        return "No Prazo"

    def __str__(self):
        return f"{self.get_fase_artefato_display()} - {self.contratacao.numero_processo}"

CATEGORIA_CONTRATO_CHOICES = [
    ('MANUTENCAO_PREDIAL', 'Manutenção Predial'),
    ('ELEVADORES', 'Elevadores'),
    ('TELEFONIA', 'Telefonia'),
    ('AUDIOVIDEO', 'Áudio e Vídeo'),
    ('TELEFONISTAS', 'Telefonistas'),
    ('GESTAO_PATRIMONIO', 'Gestão de Patrimônio'),
    ('REEMBOLSOS', 'Reembolsos'),
    ('OUTROS', 'Outros')
]

SUBCATEGORIA_PREDIAL_CHOICES = [
    ('ARQUITETURA', 'Arquitetura'),
    ('ELETRICA', 'Elétrica'),
    ('HIDRAULICA', 'Hidráulica'),
    ('CIVIL', 'Civil'),
    ('MARCENARIA', 'Marcenaria')
]

class Contratos(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="contratos"
    )
    processo_licitatorio = models.ForeignKey(
        ProcessoLicitatorio, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="contratos"
    )
    
    categoria = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Categoria do Contrato"
    )
    
    subcategoria = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name="Subcategoria (Manutenção Predial)"
    )
    
    num_contrato = models.CharField(max_length=20, default='')
    objeto = models.CharField(max_length=1000, editable=True)
    
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valor_mensal_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    inicio_vigencia = models.DateField()
    termino_vigencia = models.DateField()

    # Gestores e Fiscais da Lei 14.133
    fiscal_tecnico_titular = models.CharField(max_length=150, blank=True, null=True, verbose_name="Fiscal Técnico Titular")
    fiscal_tecnico_substituto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Fiscal Técnico Substituto")
    fiscal_admin_titular = models.CharField(max_length=150, blank=True, null=True, verbose_name="Fiscal Administrativo Titular")
    fiscal_admin_substituto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Fiscal Adm Substituto")

    # Legacy fields (mantidos para evitar perda de dados em contratos antigos)
    sei_processo = models.CharField(max_length=50, default='', blank=True, null=True)
    sei_dod = models.CharField(max_length=50, blank=True, null=True, default='')
    sei_etp = models.CharField(max_length=50, default='', blank=True, null=True)
    sei_tr = models.CharField(max_length=50, default='', blank=True, null=True)
    sei_edital = models.CharField(max_length=50, default='', blank=True, null=True)
    sei_fiscais = models.CharField(max_length=50, default='', blank=True, null=True)

    status = models.CharField(max_length=20, null=True, blank=True, default='VIGENTE')
    
    # Novos campos para gestão avançada
    contempla_postos_trabalho = models.BooleanField(default=False)

    # Configuração de Prazos de Pagamento
    dias_para_atesto = models.IntegerField(default=5, help_text="Prazo em dias para atesto da NF após a medição")
    dia_limite_pagamento = models.IntegerField(default=10, help_text="Dia limite no mês subsequente para liquidação/pagamento")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.num_contrato}"

    @property
    def valor_global_atual(self):
        soma_aditivos = sum([aditivo.valor_aditivado for aditivo in self.termos_aditivos.all()])
        return self.valor + soma_aditivos

    @property
    def valor_total_empenhado(self):
        return sum([ne.valor_atual for ne in self.notas_empenho.all() if ne.status != 'ANULADO_TOTALMENTE'])

    @property
    def saldo_a_empenhar(self):
        return self.valor_global_atual - self.valor_total_empenhado

class MedicaoMensal(models.Model):
    TIPO_CHOICES = [
        ('MENSAL', 'Mensal'),
        ('REEMBOLSO', 'Material/Serviço por Reembolso')
    ]
    contrato = models.ForeignKey(Contratos, on_delete=models.CASCADE, related_name="medicoes")
    tipo_faturamento = models.CharField(max_length=20, choices=TIPO_CHOICES, default='MENSAL')
    competencia = models.CharField(max_length=10) # Ex: 07/2026
    valor_medido = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    data_medicao = models.DateField()
    avaliador = models.CharField(max_length=150, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medição {self.competencia} - {self.contrato.num_contrato}"

class Pagamento(models.Model):
    medicao = models.OneToOneField(MedicaoMensal, on_delete=models.CASCADE, related_name="pagamento")
    
    # Protocolos
    protocolo_relatorio_mensal = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_imr = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_trd_trt = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_nf = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_nota_tecnica = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_nota_liquidacao = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_nota_sistema = models.CharField(max_length=50, blank=True, null=True, default="")
    protocolo_ordem_bancaria = models.CharField(max_length=50, blank=True, null=True, default="")

    # Valores
    valor_faturado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    porcentagem_glosa = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    porcentagem_multa = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Esse é o valor final calculado
    valor_pago = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Campos que existiam para compatibilidade/histórico (mesma logica)
    valor_glosa = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valor_multa = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(max_length=20, default='PENDENTE')
    
    FASE_CHOICES = [
        ('MEDICAO', 'Fase 1: Medição'),
        ('ATESTO', 'Fase 2: Atesto'),
        ('LIQUIDACAO', 'Fase 3: Liquidação'),
        ('PAGAMENTO', 'Fase 4: Pagamento (OB)'),
        ('CONCLUIDO', 'Concluído')
    ]
    fase_atual = models.CharField(max_length=20, choices=FASE_CHOICES, default='MEDICAO')
    
    data_conclusao_medicao = models.DateField(null=True, blank=True)
    data_conclusao_atesto = models.DateField(null=True, blank=True)
    data_conclusao_liquidacao = models.DateField(null=True, blank=True)
    
    data_pagamento = models.DateField(null=True, blank=True)
    ordem_pagamento = models.CharField(max_length=50, blank=True, null=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate calculated fields based on percentages and base value
        if self.valor_faturado is not None:
            v_faturado = Decimal(self.valor_faturado)
            p_glosa = Decimal(self.porcentagem_glosa) if self.porcentagem_glosa else Decimal('0')
            p_multa = Decimal(self.porcentagem_multa) if self.porcentagem_multa else Decimal('0')
            
            self.valor_glosa = v_faturado * (p_glosa / Decimal('100.0'))
            self.valor_multa = v_faturado * (p_multa / Decimal('100.0'))
            
            self.valor_pago = v_faturado - self.valor_glosa - self.valor_multa
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pagamento - {self.medicao.competencia}"

class TermoAditivo(models.Model):
    contrato = models.ForeignKey(Contratos, on_delete=models.CASCADE, related_name="termos_aditivos")
    numero = models.CharField(max_length=50, verbose_name="Número do Aditivo", help_text="Ex: 1/2026")
    objeto = models.TextField(blank=True, null=True, verbose_name="Objeto da Repactuação")
    
    valor_aditivado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Valor Aditivado (+ ou -)")
    novo_valor_global = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Novo Valor Global")
    
    inicio_vigencia = models.DateField(verbose_name="Início da Vigência")
    termino_vigencia = models.DateField(verbose_name="Término da Vigência")
    
    necessita_novo_termo = models.BooleanField(default=False, verbose_name="Necessita Novo Termo Aditivo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Aditivo {self.numero} - {self.contrato.num_contrato}"

class PostoTrabalho(models.Model):
    TIPO_CHOICES = [
        ('MENSALISTA', 'Mensalista'),
        ('PLANTONISTA', 'Plantonista')
    ]
    contrato = models.ForeignKey(Contratos, on_delete=models.CASCADE, related_name="postos_trabalho")
    nome_cargo = models.CharField(max_length=150, verbose_name="Posto de Trabalho (Cargo)")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='MENSALISTA')
    carga_horaria = models.CharField(max_length=50, blank=True, null=True, verbose_name="Carga Horária (Ex: 44h)")
    
    quantidade_exigida = models.IntegerField(default=1, verbose_name="Quantidade de Postos Exigida")
    
    # Valores do posto
    salario_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Salário Bruto")
    valor_hora = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Valor da Hora")
    hora_extra_50 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Hora Extra 50%")
    hora_extra_100 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Hora Extra 100%")
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Valor Unitário para Empresa (Custo Total)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def valor_total_mensal(self):
        return self.valor_unitario * self.quantidade_exigida

    def __str__(self):
        return f"{self.nome_cargo} ({self.contrato.num_contrato})"

class ItemCustoExtra(models.Model):
    contrato = models.ForeignKey(Contratos, on_delete=models.CASCADE, related_name="custos_extras")
    descricao = models.CharField(max_length=255, verbose_name="Descrição do Custo (Ex: Equipamentos, BDI)")
    valor_mensal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descricao

class Profissional(models.Model):
    pessoa = models.OneToOneField('usuarios.Pessoa', on_delete=models.CASCADE, null=True, blank=True, related_name='profissional')
    
    # Opcionalmente vincula a um técnico se for migrado para a equipe_tecnica futuramente
    tecnico_vinculado = models.ForeignKey('equipe_tecnica.Tecnico', on_delete=models.SET_NULL, null=True, blank=True, related_name='profissional_contrato')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.pessoa:
            return f"{self.pessoa.nome} - {self.pessoa.cpf or 'Sem CPF'}"
        return "Profissional Sem Pessoa"

class AlocacaoProfissional(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo')
    ]
    posto = models.ForeignKey(PostoTrabalho, on_delete=models.CASCADE, related_name="alocacoes")
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name="alocacoes")
    
    data_inicio = models.DateField(verbose_name="Data de Início na Alocação")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Fim (se inativo)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO')
    observacoes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profissional.nome} -> {self.posto.nome_cargo}"

class NotaEmpenho(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('ANULADO_PARCIALMENTE', 'Anulado Parcialmente'),
        ('ANULADO_TOTALMENTE', 'Anulado Totalmente')
    ]
    contrato = models.ForeignKey(Contratos, on_delete=models.CASCADE, related_name="notas_empenho")
    numero_ne = models.CharField(max_length=50, verbose_name="Número da Nota de Empenho (Ex: 2026NE000123)")
    
    valor_original = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valor_atual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Valor atualizado após possíveis anulações ou reforços")
    valor_anulado = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    data_emissao = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ATIVO')
    
    atualizado_via_api = models.BooleanField(default=False, help_text="Indica se os dados vieram do SIAFI")
    ultima_sincronizacao = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero_ne} - {self.contrato.num_contrato}"

