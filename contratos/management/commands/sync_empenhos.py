from django.core.management.base import BaseCommand
from contratos.models.model_contratos import NotaEmpenho
from contratos.siafi_client import SiafiClient
from django.utils import timezone

class Command(BaseCommand):
    help = 'Sincroniza os saldos das Notas de Empenho (NE) com a API do SIAFI'

    def handle(self, *args, **kwargs):
        empenhos = NotaEmpenho.objects.exclude(status='ANULADO_TOTALMENTE')
        total = empenhos.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhuma Nota de Empenho pendente de atualização.'))
            return

        client = SiafiClient()
        self.stdout.write(f'Iniciando sincronização de {total} empenhos com o SIAFI...')

        for ne in empenhos:
            self.stdout.write(f'Consultando NE: {ne.numero_ne}...')
            
            resultado = client.detalhar_empenho(ne.numero_ne)
            
            if resultado.get("sucesso"):
                ne.valor_original = resultado.get("valor_original", ne.valor_original)
                ne.valor_atual = resultado.get("valor_atual", ne.valor_atual)
                ne.valor_anulado = resultado.get("valor_anulado", ne.valor_anulado)
                ne.status = resultado.get("status", ne.status)
                
                # Update control fields
                ne.atualizado_via_api = True
                ne.ultima_sincronizacao = timezone.now()
                ne.save()
                
                self.stdout.write(self.style.SUCCESS(f'NE {ne.numero_ne} atualizada! Valor Atual: R$ {ne.valor_atual}'))
            else:
                self.stdout.write(self.style.ERROR(f'Falha ao atualizar NE {ne.numero_ne}. Erro: {resultado.get("erro")}'))

        self.stdout.write(self.style.SUCCESS('Sincronização concluída!'))
