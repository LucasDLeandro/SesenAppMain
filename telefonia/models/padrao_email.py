from django.db import models

class PadraoEmailTelefonia(models.Model):
    nome = models.CharField(max_length=100, default="Template Padrão", verbose_name="Nome do Template")
    assunto = models.CharField(max_length=200, default="Senha Telefônica", verbose_name="Assunto do E-mail")
    email_copia = models.EmailField(max_length=255, blank=True, null=True, verbose_name="E-mail em Cópia Oculta (BCC)")
    corpo = models.TextField(verbose_name="Corpo da Mensagem", help_text="Variáveis permitidas: {primeiro_nome}, {senha}, {assinatura}")
    assinatura = models.TextField(verbose_name="Assinatura da Seção", default="Seção de Equipamentos e Sistemas de Engenharia\nTelefone/Ramal: 61 3030-8224")
    ativo = models.BooleanField(default=False, verbose_name="Ativo")

    class Meta:
        verbose_name = "Padrão de E-mail de Telefonia"
        verbose_name_plural = "Padrões de E-mail de Telefonia"

    def __str__(self):
        return self.nome
