from contratos.models import *


class Contratos(models.Model):
    empresa = models.CharField(
        max_length=100,
        null=True
        )
    cnpj = models.CharField(
        max_length=50
    )
    
    num_contrato = models.CharField(
        max_length=20,
        default=''
        )
    
    objeto = models.CharField(
        max_length=1000, 
        editable=True
        )
    
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    inicio_vigencia = models.DateField()
    termino_vigencia = models.DateField()

    sei_processo = models.CharField(
        max_length = 50,
        default=''
    )

    sei_dod = models.CharField(
        max_length = 50,
        blank=True,
        default=''

    )

    sei_etp = models.CharField(
        max_length = 50,
        default=''
    )

    sei_tr = models.CharField(
        max_length = 50,
        default=''
    )

    sei_edital = models.CharField(
        max_length = 50,
        default=''
    )
    
    sei_fiscais = models.CharField(
        max_length = 50,
        default=''
    )

    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default='VIGENTE'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_At = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.num_contrato}"
