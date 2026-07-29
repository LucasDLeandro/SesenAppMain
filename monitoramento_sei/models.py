from django.db import models
from contratos.models.model_contratos import Contratos, ProcessoLicitatorio
from empresas.models import Empresa

class ProcessoSEI(models.Model):
    TIPO_CHOICES = [
        ('PRIORITARIO', 'Prioritário'),
        ('TRAMITE', 'Em Trâmite'),
        ('CONCLUIDO', 'Concluído')
    ]

    numero_processo = models.CharField(max_length=50, unique=True, verbose_name="Número do Processo (SEI)")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='TRAMITE', verbose_name="Tipo de Monitoramento")
    
    # Metadados obtidos da API do SEI
    data_autuacao = models.DateField(blank=True, null=True, verbose_name="Data de Recebimento / Autuação")
    objeto = models.TextField(blank=True, null=True, verbose_name="Objeto (Especificação)")
    
    # Tratativas / Situação atual (último andamento)
    situacao_atual = models.TextField(blank=True, null=True, verbose_name="Situação / Tratativa Atual")
    tempo_tramitacao = models.IntegerField(default=0, verbose_name="Tempo de Tramitação (dias)")
    ultimo_andamento_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID do Último Andamento")
    
    # Vínculos com o resto do sistema
    contrato = models.ForeignKey(Contratos, on_delete=models.SET_NULL, null=True, blank=True, related_name="processos_sei")
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name="processos_sei")
    processo_licitatorio = models.ForeignKey(ProcessoLicitatorio, on_delete=models.SET_NULL, null=True, blank=True, related_name="processos_sei")

    # Controle de Sincronização
    ultima_sincronizacao = models.DateTimeField(auto_now=True, verbose_name="Última Sincronização")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero_processo} - {self.tipo}"

class HistoricoAndamento(models.Model):
    processo = models.ForeignKey(ProcessoSEI, on_delete=models.CASCADE, related_name="historico_andamentos")
    id_andamento_sei = models.CharField(max_length=50)
    data_hora = models.DateTimeField()
    descricao = models.TextField()
    unidade = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.processo.numero_processo} - {self.data_hora}"
