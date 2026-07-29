from notificacoes.models import *

class Contato(models.Model):
    pessoa = models.ForeignKey('usuarios.Pessoa', on_delete=models.CASCADE, null=True, blank=True, related_name="contatos_notificacao")
    
    @property
    def nome(self):
        return self.pessoa.nome if self.pessoa else ''

    @property
    def telefone(self):
        return self.pessoa.telefone if self.pessoa else ''
    role=models.CharField(
        max_length = 100,
        default='Geral',
        verbose_name='Tipo de Contato'
    )

    notifica_elevadores = models.BooleanField(
        default=True,
        verbose_name='Recebe de Elevadores'
    )
    
    notifica_telefonia = models.BooleanField(
        default=False,
        verbose_name='Recebe de Telefonia'
    )
    
    receber_whatsapp = models.BooleanField(
        default=True,
        verbose_name='Receber via WhatsApp'
    )
    
    receber_email = models.BooleanField(
        default=False,
        verbose_name='Receber via E-mail'
    )

    is_ativo=models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )
    updated_at=models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.nome}"