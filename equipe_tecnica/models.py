from django.db import models
from empresas.models import Empresa

class Tecnico(models.Model):
    pessoa = models.ForeignKey('usuarios.Pessoa', on_delete=models.CASCADE, null=True, blank=True, related_name="tecnicos")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="tecnicos")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def nome(self):
        return self.pessoa.nome if self.pessoa else ''

    @property
    def cpf(self):
        return self.pessoa.cpf if self.pessoa else ''

    @property
    def telefone(self):
        return self.pessoa.telefone if self.pessoa else ''

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

class SolicitacaoAcesso(models.Model):
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('expirada', 'Expirada'),
        ('revogada', 'Revogada'),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="solicitacoes_acesso")
    nome_solicitante = models.CharField(max_length=255, verbose_name="Nome do Solicitante")
    data_solicitacao = models.DateField(verbose_name="Data da Solicitação")
    validade_inicio = models.DateField(verbose_name="Validade (Início)")
    validade_fim = models.DateField(verbose_name="Validade (Fim)")
    
    tecnicos = models.ManyToManyField(Tecnico, related_name="solicitacoes_vinculadas", verbose_name="Técnicos Autorizados")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitação: {self.empresa.nome_empresa} ({self.validade_inicio} a {self.validade_fim})"

class PadraoEmailLiberacao(models.Model):
    nome = models.CharField(max_length=100, default="Template Padrão", verbose_name="Nome do Template")
    assunto = models.CharField(max_length=200, default="Liberação de Acesso", verbose_name="Assunto do E-mail")
    email_destinatario = models.EmailField(max_length=255, blank=True, null=True, verbose_name="E-mail Destinatário (Segurança/Portaria)", help_text="E-mail principal que receberá as comunicações de liberação de acesso")
    email_copia = models.EmailField(max_length=255, blank=True, null=True, verbose_name="E-mail em Cópia Oculta (BCC)")
    corpo = models.TextField(verbose_name="Corpo da Mensagem", help_text="Variáveis permitidas: {empresa}, {solicitante}, {periodo}, {datas}, {tecnicos}")
    assinatura = models.TextField(verbose_name="Assinatura da Seção", default="Equipe Técnica")
    ativo = models.BooleanField(default=False, verbose_name="Ativo")

    class Meta:
        verbose_name = "Padrão de E-mail de Liberação"
        verbose_name_plural = "Padrões de E-mail de Liberação"

    def __str__(self):
        return self.nome

class LiberacaoAcessoDiaria(models.Model):
    PERIODO_CHOICES = [
        ('Manhã', 'Matutino'),
        ('Tarde', 'Vespertino'),
        ('Integral', 'Integral'),
        ('Noturno', 'Noturno'),
    ]

    solicitacao = models.ForeignKey(SolicitacaoAcesso, on_delete=models.CASCADE, related_name="liberacoes_diarias")
    tecnicos = models.ManyToManyField(Tecnico, related_name="liberacoes_presentes")
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim")
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, default='Integral')
    
    email_enviado = models.BooleanField(default=False)
    data_agendamento_email = models.DateTimeField(null=True, blank=True, verbose_name="Envio Programado")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Liberação: {self.solicitacao.empresa.nome_empresa} ({self.data_inicio} - {self.periodo})"
