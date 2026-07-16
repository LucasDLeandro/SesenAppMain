from django.contrib import admin

# Register your models here.
from .models.solicitacao_aparelho import TelefoneSolicitacao
from .models.aparelhos_telefonicos import AparelhoVoip
from .models.remessa_manutencao import RemessaManutencao
from .models.solicitacao_senha import CriarSenha

admin.site.register(TelefoneSolicitacao)
admin.site.register(AparelhoVoip)
admin.site.register(RemessaManutencao)
admin.site.register(CriarSenha)