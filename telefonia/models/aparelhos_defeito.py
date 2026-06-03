from telefonia.models import *

class AparelhoDefeito(models.Model):

    aparelho = models.ForeignKey(
        AparelhoVoip, 
        on_delete=models.SET_NULL,
        related_name="historico_defeitos",
        null=True
    )

    data_defeito = models.DateTimeField()
    
    defeito = models.CharField(
        max_length=500,
        null=True
    )

    data_retirada_plaqueta = models.DateTimeField()

    memo_solicitacao_baixa = models.DateTimeField()

    data_baixa_patrimonio = models.DateTimeField()

    data_saida_manutencao = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.aparelho}"

    

