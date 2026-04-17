from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from notificacoes.models.template_notificacao import TemplateMessage
from notificacoes.forms.template_message_form import CriarTemplateForm

@require_POST
def api_criar_template(request):
    form = CriarTemplateForm(request.POST)

    if form.is_valid():
        novo_template = form.save()

        return JsonResponse({
            'sucesso': True,
            'mensagem': f"Template: {novo_template.id_template}, criado com sucesso!"
        })
    
    return JsonResponse({
        'sucesso': False,
        'errors': form.errors
    }, status=400)

@require_POST
def api_editar_template(request, id_template):
    template_existente = get_object_or_404(TemplateMessage, pk=id_template)

    form = CriarTemplateForm(request.POST, instance=template_existente)

    if form.is_valid():
        form.save()
        
        evento = form.cleaned_data['tipo_evento']
        template = get_object_or_404(TemplateMessage, tipo_evento=evento)
        texto = template.base_text
        print(texto)

        return JsonResponse({
            'sucesso': True,
            'mensagem': f"Template: {template_existente.id_template}, atualizado com sucesso!"
        })
    return JsonResponse({
        'sucesso': False,
        'mensagem': f"Erros encontrados: {form.errors}"
    }, status=400)

@require_POST
def api_deletar_template(request, id_template):
    template_existente = get_object_or_404(TemplateMessage, pk=id_template)

    template_existente.delete()
    
    return JsonResponse({
        'sucesso': True,
        'mensagem': f"O template foi excluido com sucesso!"
    })