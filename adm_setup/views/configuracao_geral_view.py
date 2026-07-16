from django.shortcuts import render, redirect
from django.contrib import messages
from adm_setup.models import ConfiguracaoGeral

def configuracao_geral_view(request):
    config = ConfiguracaoGeral.get_instance()
    
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
            
        return redirect('adm_setup:configuracao_geral')
        
    return render(request, 'setups/configuracao_geral.html', {'config': config})
