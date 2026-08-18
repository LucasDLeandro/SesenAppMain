from django.db import models

class PadraoNadaConstaTelefonia(models.Model):
    nome = models.CharField(
        max_length=100,
        default="Template Padrão",
        verbose_name="Nome do Template"
    )
    cabecalho_logo = models.CharField(
        max_length=150, 
        default="TRIBUNAL SUPERIOR ELEITORAL", 
        verbose_name="Cabeçalho: Órgão Principal"
    )
    cabecalho_sublogo1 = models.CharField(
        max_length=150, 
        default="SECRETARIA DE TECNOLOGIA DA INFORMAÇÃO", 
        verbose_name="Cabeçalho: Secretaria"
    )
    cabecalho_sublogo2 = models.CharField(
        max_length=150, 
        default="SEÇÃO DE TELEFONIA", 
        verbose_name="Cabeçalho: Seção"
    )
    titulo_documento = models.CharField(
        max_length=150, 
        default="INFORMATIVO DE DÉBITO - TELEFONIA", 
        verbose_name="Título do Documento"
    )
    
    paragrafo_introdutorio = models.TextField(
        default='Em resposta à solicitação de Nada Consta (Protocolo SEI nº {protocolo}), informamos que após verificação no sistema de tarifação desta Seção de Telefonia, foi constatado débito pendente em nome do(a) servidor(a) {servidor}, da unidade {unidade} ({sigla_unidade}).',
        verbose_name="Parágrafo Introdutório",
        help_text="Use as tags {protocolo}, {servidor}, {unidade}, {sigla_unidade} para substituir dinamicamente."
    )
    paragrafo_dados_vinculados = models.TextField(
        default='Os dados vinculados ao servidor no sistema são:\nRamal: {ramal}\nE-mail Cadastrado: {email}',
        verbose_name="Dados Vinculados",
        help_text="Use as tags {ramal}, {email}."
    )
    
    descricao_debito = models.CharField(
        max_length=255, 
        default="Débito referente à utilização do sistema de telefonia (faturas pendentes)",
        verbose_name="Descrição do Débito (Tabela)"
    )
    
    paragrafo_conclusao = models.TextField(
        default='Solicita-se que o referido valor seja recolhido via Guia de Recolhimento da União (GRU) e o comprovante anexado ao processo SEI para a devida quitação e emissão do Nada Consta definitivo.',
        verbose_name="Parágrafo Conclusivo"
    )

    assinatura_secao = models.CharField(
        max_length=150,
        default="Seção de Telefonia - TSE",
        verbose_name="Assinatura: Seção"
    )
    assinatura_local = models.CharField(
        max_length=150,
        default="Brasília, {data}",
        verbose_name="Assinatura: Local e Data",
        help_text="Use {data} para a data atual formatada."
    )
    
    ativo = models.BooleanField(
        default=True, 
        help_text="Apenas o padrão marcado como ATIVO será exibido na geração dos PDFs de fatura de Nada Consta."
    )

    class Meta:
        verbose_name = "Padrão de Documento (Nada Consta)"
        verbose_name_plural = "Padrões de Documento (Nada Constas)"

    def save(self, *args, **kwargs):
        if self.ativo:
            # Se este estiver sendo salvo como ativo, desativa todos os outros
            PadraoNadaConstaTelefonia.objects.filter(ativo=True).update(ativo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Ativo" if self.ativo else "Inativo"
        return f"{self.nome} ({status})"
