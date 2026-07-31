from django.shortcuts import render, redirect
from django.contrib import messages
from telefonia.models import PadraoSenhaTelefonia
from telefonia.models import PadraoTutorialTelefonia
from telefonia.models import PadraoEmailTelefonia
from reembolsos.models import ConfiguracaoRelatorio
from notificacoes.models.template_notificacao import TemplateMessage

def configuracao_telefonia_view(request):
    if not PadraoSenhaTelefonia.objects.exists():
        PadraoSenhaTelefonia.objects.create(nome="Template Padrão Senha", ativo=True)
    if not PadraoTutorialTelefonia.objects.exists():
        PadraoTutorialTelefonia.objects.create(nome="Tutorial Padrão", ativo=True)
    if not PadraoEmailTelefonia.objects.exists():
        PadraoEmailTelefonia.objects.create(nome="Template Padrão Email", ativo=True)
    
    # Garantir a existência dos templates de WhatsApp de Telefonia
    if not TemplateMessage.objects.filter(tipo_evento='tel_solicitacao_aparelho').exists():
        TemplateMessage.objects.create(
            tipo_evento='tel_solicitacao_aparelho',
            id_template='TEL_APARELHO_TEMPLATE',
            base_text='Olá {solicitante},\n\nSua solicitação do protocolo {protocolo} referente ao aparelho telefônico do(a) {unidade}, no setor {setor}, foi concluída.'
        )
    if not TemplateMessage.objects.filter(tipo_evento='tel_solicitacao_senha').exists():
        TemplateMessage.objects.create(
            tipo_evento='tel_solicitacao_senha',
            id_template='TEL_SENHA_TEMPLATE',
            base_text='Olá {solicitante},\n\nSua solicitação do protocolo {protocolo} referente à senha telefônica do(a) {unidade} foi concluída.'
        )
    if not TemplateMessage.objects.filter(tipo_evento='tel_recolhimento_evento').exists():
        TemplateMessage.objects.create(
            tipo_evento='tel_recolhimento_evento',
            id_template='TEL_RECOLHIMENTO_EVENTO_TEMPLATE',
            base_text='⚠️ *LEMBRETE DE RECOLHIMENTO*\n\nO evento *{evento_nome}* tem recolhimento de aparelhos previsto para o prazo limite.\nData Fim: {data_fim}\nLocal: {local}\nSolicitante: {solicitante}\n\nPor favor, acesse a Dashboard de Telefonia no SesenApp para efetuar a baixa.'
        )

    templates_senha = PadraoSenhaTelefonia.objects.all().order_by('-id')
    templates_tutorial = PadraoTutorialTelefonia.objects.all().order_by('-id')
    templates_email = PadraoEmailTelefonia.objects.all().order_by('-id')
    templates_whatsapp = TemplateMessage.objects.filter(tipo_evento__in=['tel_solicitacao_aparelho', 'tel_solicitacao_senha', 'tel_recolhimento_evento']).order_by('-id')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # --- SENHAS ---
        if action == 'save_senha_template':
            template_id = request.POST.get('template_id')
            if template_id:
                template_obj = PadraoSenhaTelefonia.objects.filter(id=template_id).first()
                if not template_obj: template_obj = PadraoSenhaTelefonia()
            else:
                template_obj = PadraoSenhaTelefonia()
                
            template_obj.nome = request.POST.get('nome', template_obj.nome)
            template_obj.cabecalho_logo = request.POST.get('cabecalho_logo', template_obj.cabecalho_logo)
            template_obj.cabecalho_sublogo = request.POST.get('cabecalho_sublogo', template_obj.cabecalho_sublogo)
            template_obj.cabecalho_subtitulo = request.POST.get('cabecalho_subtitulo', template_obj.cabecalho_subtitulo)
            template_obj.instrucoes_celular = request.POST.get('instrucoes_celular', template_obj.instrucoes_celular)
            template_obj.instrucoes_interurbanas = request.POST.get('instrucoes_interurbanas', template_obj.instrucoes_interurbanas)
            template_obj.instrucoes_internacionais = request.POST.get('instrucoes_internacionais', template_obj.instrucoes_internacionais)
            template_obj.termo_obrigatorio = request.POST.get('termo_obrigatorio', template_obj.termo_obrigatorio)
            template_obj.termo_ligacoes_longa_distancia = request.POST.get('termo_ligacoes_longa_distancia', template_obj.termo_ligacoes_longa_distancia)
            template_obj.termo_ressarcimento = request.POST.get('termo_ressarcimento', template_obj.termo_ressarcimento)
            template_obj.ativo = request.POST.get('ativo') == 'on'
            template_obj.save()
            
            messages.success(request, 'Configurações do Modelo de Senha salvas com sucesso!')
            return redirect('adm_setup:configuracao_telefonia')
            
        elif action == 'delete_senha_template':
            template_id = request.POST.get('template_id')
            if template_id:
                PadraoSenhaTelefonia.objects.filter(id=template_id).delete()
                messages.success(request, 'Template de Senha excluído com sucesso!')
            return redirect('adm_setup:configuracao_telefonia')

        # --- TUTORIAIS ---
        elif action == 'save_tutorial_template':
            template_id = request.POST.get('template_id')
            if template_id:
                template_obj = PadraoTutorialTelefonia.objects.filter(id=template_id).first()
                if not template_obj: template_obj = PadraoTutorialTelefonia()
            else:
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
            return redirect('adm_setup:configuracao_telefonia')
            
        elif action == 'delete_tutorial_template':
            template_id = request.POST.get('template_id')
            if template_id:
                PadraoTutorialTelefonia.objects.filter(id=template_id).delete()
                messages.success(request, 'Template de Tutorial excluído com sucesso!')
            return redirect('adm_setup:configuracao_telefonia')
        # --- EMAILS ---
        elif action == 'save_email_template':
            template_id = request.POST.get('template_id')
            if template_id:
                template_obj = PadraoEmailTelefonia.objects.filter(id=template_id).first()
                if not template_obj: template_obj = PadraoEmailTelefonia()
            else:
                template_obj = PadraoEmailTelefonia()
                
            template_obj.nome = request.POST.get('nome', template_obj.nome)
            template_obj.assunto = request.POST.get('assunto', template_obj.assunto)
            template_obj.email_copia = request.POST.get('email_copia', template_obj.email_copia)
            template_obj.corpo = request.POST.get('corpo', template_obj.corpo)
            template_obj.assinatura = request.POST.get('assinatura', template_obj.assinatura)
            template_obj.ativo = request.POST.get('ativo') == 'on'
            template_obj.save()
            
            messages.success(request, 'Configurações de E-mail salvas com sucesso!')
            return redirect('adm_setup:configuracao_telefonia')
            
        elif action == 'delete_email_template':
            template_id = request.POST.get('template_id')
            if template_id:
                PadraoEmailTelefonia.objects.filter(id=template_id).delete()
                messages.success(request, 'Template de E-mail excluído com sucesso!')
            return redirect('adm_setup:configuracao_telefonia')
            
        # --- WHATSAPP ---
        elif action == 'save_whatsapp_template':
            template_id = request.POST.get('template_id')
            if template_id:
                template_obj = TemplateMessage.objects.filter(id=template_id).first()
                if template_obj:
                    template_obj.base_text = request.POST.get('mensagem', template_obj.base_text)
                    template_obj.save()
                    messages.success(request, 'Template de WhatsApp atualizado com sucesso!')
            return redirect('adm_setup:configuracao_telefonia')
        
    config_reembolsos, _ = ConfiguracaoRelatorio.objects.get_or_create(id=1)

    return render(request, 'setups/configuracao_telefonia.html', {
        'templates_senha': templates_senha,
        'templates_tutorial': templates_tutorial,
        'templates_email': templates_email,
        'templates_whatsapp': templates_whatsapp,
        'config_reembolsos': config_reembolsos
    })
