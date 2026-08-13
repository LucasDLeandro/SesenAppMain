from django.shortcuts import render, redirect
from django.contrib import messages
from adm_setup.models import ConfiguracaoGeral, AgendamentoTask

def configuracao_geral_view(request):
    config = ConfiguracaoGeral.get_instance()
    
    # Inicia a tarefa padrão se não existir
    AgendamentoTask.objects.get_or_create(
        task_id='notificar_eventos_expirados',
        defaults={
            'nome_amigavel': 'Verificar Eventos Pendentes (Telefonia)',
            'intervalo_minutos': 60,
            'ativo': True
        }
    )
    AgendamentoTask.objects.get_or_create(
        task_id='enviar_emails_liberacao',
        defaults={
            'nome_amigavel': 'Enviar E-mails Agendados (Equipe Técnica)',
            'intervalo_minutos': 1,
            'ativo': True
        }
    )
    
    rotinas = AgendamentoTask.objects.all().order_by('nome_amigavel')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_global':
            config.notificar_novos_usuarios = request.POST.get('notificar_novos_usuarios') == 'on'
            config.save()
            messages.success(request, 'Configurações Globais atualizadas com sucesso!')
            
        elif action == 'save_template':
            config.mensagem_boas_vindas = request.POST.get('mensagem_boas_vindas')
            config.save()
            messages.success(request, 'Template de Boas-Vindas atualizado com sucesso!')
            
        elif action == 'save_agendamento':
            task_id = request.POST.get('task_id')
            intervalo = request.POST.get('intervalo_minutos')
            ativo = request.POST.get('ativo') == 'on'
            
            task = AgendamentoTask.objects.filter(task_id=task_id).first()
            if task:
                task.intervalo_minutos = int(intervalo)
                task.ativo = ativo
                task.save()
                
                # Reagendar a tarefa no APScheduler
                try:
                    from telefonia.scheduler import scheduler
                    from telefonia.tasks import verificar_e_notificar_eventos
                    
                    # Como no futuro podem existir outras tasks, fazemos um IF básico aqui
                    if task.task_id == 'notificar_eventos_expirados':
                        if scheduler.get_job('job_notificar_eventos_expirados'):
                            if task.ativo:
                                scheduler.reschedule_job('job_notificar_eventos_expirados', trigger='interval', minutes=task.intervalo_minutos)
                                scheduler.resume_job('job_notificar_eventos_expirados')
                            else:
                                scheduler.pause_job('job_notificar_eventos_expirados')
                        else:
                            if task.ativo:
                                scheduler.add_job(verificar_e_notificar_eventos, 'interval', minutes=task.intervalo_minutos, id='job_notificar_eventos_expirados', replace_existing=True)
                    
                    elif task.task_id == 'enviar_emails_liberacao':
                        if scheduler.get_job('job_enviar_emails_liberacao'):
                            if task.ativo:
                                scheduler.reschedule_job('job_enviar_emails_liberacao', trigger='interval', minutes=task.intervalo_minutos)
                                scheduler.resume_job('job_enviar_emails_liberacao')
                            else:
                                scheduler.pause_job('job_enviar_emails_liberacao')
                        else:
                            if task.ativo:
                                from django.core.management import call_command
                                def run_enviar_emails_liberacao():
                                    call_command('enviar_emails_liberacao')
                                scheduler.add_job(run_enviar_emails_liberacao, 'interval', minutes=task.intervalo_minutos, id='job_enviar_emails_liberacao', replace_existing=True)
                except Exception as e:
                    messages.error(request, f'Rotina salva, mas erro ao atualizar agendamento em memória: {e}')
                
                messages.success(request, 'Configuração da rotina atualizada com sucesso!')
            
        return redirect('adm_setup:configuracao_geral')
        
    return render(request, 'setups/configuracao_geral.html', {'config': config, 'rotinas': rotinas})
