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
        default='Geral'
    )

    is_ativo=models.BooleanField(
        default=True
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )
    updated_at=models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.nome}"