from django.shortcuts import render
from django.http import JsonResponse
import json
from notificacoes.models.contato_notificacao import Contato
from notificacoes.models.template_notificacao import TemplateMessage
from notificacoes.forms.contato_form import CriarContatoForm

def gerenciar_notificacao(request):
    list_contato = Contato.objects.all()
    list_message = TemplateMessage.objects.all()
    criar_contato = CriarContatoForm()

    template = 'messages/gerenciar_contatos_e_templates.html'

    context = {
            'list_contato': list_contato,
            'list_template': list_message,
            'criarContato': criar_contato
        }
    
    return render(request, template, context)



    