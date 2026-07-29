from django.core.management.base import BaseCommand
from monitoramento_sei.models import ProcessoSEI, HistoricoAndamento
from monitoramento_sei.sei_client import SeiClient
from datetime import datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Sincroniza os processos SEI cadastrados com a API do SEI.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando sincronização com o SEI...')
        
        client = SeiClient()
        if not client.client:
            self.stdout.write(self.style.ERROR('Não foi possível inicializar o cliente SEI. Verifique credenciais e URL.'))
            return
            
        processos = ProcessoSEI.objects.all()
        for processo in processos:
            self.stdout.write(f'Sincronizando processo {processo.numero_processo}...')
            
            # TODO: Quando o SEI estiver configurado, descomente o bloco abaixo para realizar chamadas reais
            
            """
            # 1. Pega info básica (opcional, para atualizar objeto)
            info = client.get_processo_info(processo.numero_processo)
            if info:
                # Tratar dados do info e salvar no processo
                # processo.objeto = info['Especificacao']
                pass
                
            # 2. Pega andamentos
            andamentos = client.get_andamentos(processo.numero_processo)
            if andamentos and len(andamentos) > 0:
                # Pega o andamento mais recente
                ultimo = andamentos[-1] 
                
                processo.situacao_atual = ultimo.get('Descricao', '')
                processo.ultimo_andamento_id = ultimo.get('IdAndamento', '')
                
                # Exemplo simples de gravar no histórico
                HistoricoAndamento.objects.get_or_create(
                    processo=processo,
                    id_andamento_sei=ultimo.get('IdAndamento', ''),
                    defaults={
                        'data_hora': timezone.now(), # Idealmente vem do WSDL (ultimo.DataHora)
                        'descricao': ultimo.get('Descricao', ''),
                        'unidade': ultimo.get('Unidade', {}).get('Sigla', ''),
                    }
                )
            """
            
            # Por enquanto, apenas atualizamos a data da última sincronização
            processo.save()
            
        self.stdout.write(self.style.SUCCESS('Sincronização concluída.'))
