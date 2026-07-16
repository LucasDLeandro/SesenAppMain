from django.shortcuts import render, redirect
from django.contrib import messages
from telefonia.models import PadraoTutorialTelefonia

def configuracao_tutorial_telefonia_view(request):
    if not PadraoTutorialTelefonia.objects.exists():
        PadraoTutorialTelefonia.objects.create(nome="Tutorial Padrão", ativo=True)

    templates = PadraoTutorialTelefonia.objects.all().order_by('-id')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_template':
            template_id = request.POST.get('template_id')
            if template_id:
                # Editar existente
                template_obj = PadraoTutorialTelefonia.objects.filter(id=template_id).first()
                if not template_obj:
                    template_obj = PadraoTutorialTelefonia()
            else:
                # Novo template
                template_obj = PadraoTutorialTelefonia()
                
            template_obj.nome = request.POST.get('nome', template_obj.nome)
            template_obj.cabecalho_logo = request.POST.get('cabecalho_logo', template_obj.cabecalho_logo)
            template_obj.cabecalho_sublogo = request.POST.get('cabecalho_sublogo', template_obj.cabecalho_sublogo)
            template_obj.cabecalho_subtitulo = request.POST.get('cabecalho_subtitulo', template_obj.cabecalho_subtitulo)
            template_obj.introducao = request.POST.get('introducao', template_obj.introducao)
            template_obj.exemplo_email = request.POST.get('exemplo_email', template_obj.exemplo_email)
            template_obj.secao_validacao = request.POST.get('secao_validacao', template_obj.secao_validacao)
            template_obj.secao_pagamento = request.POST.get('secao_pagamento', template_obj.secao_pagamento)
            template_obj.secao_consequencias = request.POST.get('secao_consequencias', template_obj.secao_consequencias)
            template_obj.secao_duvidas = request.POST.get('secao_duvidas', template_obj.secao_duvidas)
            template_obj.ativo = request.POST.get('ativo') == 'on'
            template_obj.save()
            
            messages.success(request, 'Configurações do Tutorial salvas com sucesso!')
            return redirect('adm_setup:configuracao_tutorial')
            
        elif action == 'delete_template':
            template_id = request.POST.get('template_id')
            if template_id:
                PadraoTutorialTelefonia.objects.filter(id=template_id).delete()
                messages.success(request, 'Template de Tutorial excluído com sucesso!')
            return redirect('adm_setup:configuracao_tutorial')

    context = {
        'templates': templates,
    }
    return render(request, 'setups/configuracao_tutorial.html', context)
