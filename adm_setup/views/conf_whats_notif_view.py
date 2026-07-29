from django.shortcuts import render
from django.http import JsonResponse
import json
from notificacoes.models.contato_notificacao import Contato
from notificacoes.models.template_notificacao import TemplateMessage
from notificacoes.forms.contato_form import CriarContatoForm
from notificacoes.forms.template_message_form import CriarTemplateForm

def gerenciar_notificacao(request):
    list_contato_elev = Contato.objects.filter(notifica_elevadores=True)
    list_contato_tel = Contato.objects.filter(notifica_telefonia=True)
    
    list_message_elev = TemplateMessage.objects.exclude(tipo_evento__startswith='tel_')
    list_message_tel = TemplateMessage.objects.filter(tipo_evento__startswith='tel_')
    
    criar_contato = CriarContatoForm()
    criar_template = CriarTemplateForm()

    template = 'messages/gerenciar_contatos_e_templates.html'

    context = {
            'list_contato_elev': list_contato_elev,
            'list_contato_tel': list_contato_tel,
            'list_template_elev': list_message_elev,
            'list_template_tel': list_message_tel,
            'criarContato': criar_contato,
            'criarTemplate': criar_template
        }
    
    return render(request, template, context)



    