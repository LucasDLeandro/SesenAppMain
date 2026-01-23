from service_orders.models import *

class Empresa(models.Model):
    nome=models.CharField()
    cnpj=models.CharField()
    contrato=models.CharField()
    sei_contratacao=models.CharField()
    dod=models.CharField()
    etp=models.CharField()
    tr=models.CharField()
    edital=models.CharField()
    contrato_assinado=models.CharField()
    valor_contrato=models.CharField()
    designacao_fiscais=models.CharField()
