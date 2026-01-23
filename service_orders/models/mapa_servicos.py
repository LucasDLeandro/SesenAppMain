from service_orders.models import *

class Categoria(models.Model):
    nome_categoria = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        default="")
    
    descricao_categoria = models.TextField(
        blank=True,
        null=False,
        default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_categoria or ""
    
class Servico(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='servicos')
    
    nome_servico = models.CharField(
        max_length=100,
        blank=True,
        null=False,
        default="")

    descricao_servico = models.TextField(
        blank=True,
        null=False,
        default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.categoria}, {self.nome_servico}"