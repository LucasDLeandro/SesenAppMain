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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.num_contrato}"

class MedicaoMensal(models.Model):
    contrato = models.ForeignKey(Contratos, on_delete=models.CASCADE, related_name="medicoes")
    competencia = models.CharField(max_length=10) # Ex: 07/2026
    valor_medido = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    data_medicao = models.DateField()
    avaliador = models.CharField(max_length=150, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medição {self.competencia} - {self.contrato.num_contrato}"

class Pagamento(models.Model):
    medicao = models.OneToOneField(MedicaoMensal, on_delete=models.CASCADE, related_name="pagamento")
    valor_pago = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valor_glosa = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valor_multa = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(max_length=20, default='PENDENTE')
    data_pagamento = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pagamento - {self.medicao.competencia}"
