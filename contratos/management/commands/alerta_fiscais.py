from django.core.management.base import BaseCommand
from datetime import date
from contratos.models import Contratos, MedicaoMensal

class Command(BaseCommand):
    help = 'Gera relatórios/alertas para fiscais sobre pagamentos em atraso do mês atual'

    def handle(self, *args, **kwargs):
        hoje = date.today()
        competencia_atual = f"{str(hoje.month).zfill(2)}/{str(hoje.year)}"
        
        contratos_vigentes = Contratos.objects.filter(status='VIGENTE')
        atrasados = []
        
        for contrato in contratos_vigentes:
            medicao = MedicaoMensal.objects.filter(contrato=contrato, competencia=competencia_atual).first()
            if medicao and hasattr(medicao, 'pagamento'):
                pag = medicao.pagamento
                if pag.fase_atual != 'CONCLUIDO':
                    if hoje.day > contrato.dia_limite_pagamento:
                        atrasados.append(f"Contrato {contrato.num_contrato} - FASE: {pag.fase_atual} (Limite era dia {contrato.dia_limite_pagamento})")
            else:
                if hoje.day > contrato.dias_para_atesto:
                    atrasados.append(f"Contrato {contrato.num_contrato} - SEM MEDIÇÃO ESTE MÊS (Atrasado)")
                    
        if atrasados:
            self.stdout.write(self.style.WARNING(f"Existem {len(atrasados)} contratos com pendências no fluxo de pagamento:"))
            for a in atrasados:
                self.stdout.write(self.style.ERROR(" - " + a))
                
            # To-Do: Integrar com e-mail, WhatsApp ou sistema de notificação in-app.
            self.stdout.write(self.style.SUCCESS("Alertas listados com sucesso!"))
        else:
            self.stdout.write(self.style.SUCCESS("Nenhum contrato em atraso neste mês! Tudo no prazo."))
