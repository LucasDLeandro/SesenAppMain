from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from notificacoes.models.contato_notificacao import Contato
from notificacoes.forms.contato_form import CriarContatoForm
from notificacoes.models.template_notificacao import TemplateMessage


@require_POST
def api_criar_contato(request):
    form = CriarContatoForm(request.POST)
    
    if form.is_valid():
        novo_contato = form.save()

        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Contato: {novo_contato.nome}, criado com sucesso!'
        })
    
    return JsonResponse({
        'sucesso': False,
        'erros': form.errors
    }, status=400)


@require_POST
def api_editar_contato(request, id_contato):

    contato_existente = get_object_or_404(Contato, pk=id_contato)

    form = CriarContatoForm(request.POST, instance=contato_existente)

    if form.is_valid():
        form.save()

        return JsonResponse({
            'sucesso': True,
            'mensagem': f'Contato: {contato_existente.nome}, atualizado com sucesso!'
        })
    return JsonResponse({
        'sucesso': False,
        'mensagem': f'Erros encontrados: {form.errors}'
    }, status=400)