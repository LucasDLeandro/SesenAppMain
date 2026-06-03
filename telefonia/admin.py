from django.contrib import admin

# Register your models here.
from .models.solicitacao_aparelho import TelefoneSolicitacao
from .models.aparelhos_telefonicos import AparelhoVoip
from .models.aparelhos_defeito import AparelhoDefeito
from .models.solicitacao_senha import CriarSenha

admin.site.register(TelefoneSolicitacao)
admin.site.register(AparelhoVoip)
admin.site.register(AparelhoDefeito)
admin.site.register(CriarSenha)