import logging
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from telefonia.tasks import verificar_e_notificar_eventos
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

# Instância global para poder ser importada e alterada pela View
scheduler = BackgroundScheduler()

def start():
    # Evita que o scheduler seja iniciado mais de uma vez quando o Django usa o auto-reloader (runserver)
    if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
        return

    from adm_setup.models import AgendamentoTask
    try:
        task, created = AgendamentoTask.objects.get_or_create(
            task_id='notificar_eventos_expirados',
            defaults={
                'nome_amigavel': 'Verificar Eventos Pendentes (Telefonia)',
                'intervalo_minutos': 60,
                'ativo': True
            }
        )
        intervalo = task.intervalo_minutos
        ativo = task.ativo
    except (OperationalError, ProgrammingError):
        # Banco não está pronto ainda ou migração pendente
        intervalo = 60
        ativo = True

    if ativo:
        scheduler.add_job(verificar_e_notificar_eventos, 'interval', minutes=intervalo, id='job_notificar_eventos_expirados', replace_existing=True)
    
    # scheduler.start() precisa ser executado, mas com cautela em produção se houver vários workers.
    scheduler.start()
    logger.info(f"APScheduler iniciado: tarefa 'verificar_e_notificar_eventos' {'configurada' if ativo else 'pausada'}, intervalo {intervalo} mins.")
