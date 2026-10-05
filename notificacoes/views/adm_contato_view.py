from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from notificacoes.models.contato_notificacao import Contato
from notificacoes.forms.contato_form import CriarContatoForm



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

@require_POST
def api_deletar_contato(request, id_contato):
    contato_existente = get_object_or_404(Contato, pk=id_contato)

    contato_existente.delete()

    
    return JsonResponse({
        'sucesso': True,
        'mensagem': f"O contato foi excluido com sucesso!"
    })

@require_POST
def api_bulk_status_contato(request):
    import json
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        acao = data.get('acao') # 'ativar' or 'desativar'
        
        if not ids or acao not in ['ativar', 'desativar']:
            return JsonResponse({'sucesso': False, 'mensagem': 'Dados inválidos.'}, status=400)
            
        status_value = (acao == 'ativar')
        
        # O Django's update() method runs a single SQL UPDATE query for bulk updates
        Contato.objects.filter(id__in=ids).update(is_ativo=status_value)
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': f"{len(ids)} contato(s) {'ativado' if status_value else 'desativado'}(s) com sucesso!"
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)}, status=500)

def api_buscar_pessoas(request):
    """Retorna JSON com as pessoas correspondentes à busca para autocomplete."""
    from usuarios.models import Pessoa
    from django.contrib.auth.models import User
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return JsonResponse({'pessoas': []})
    
    pessoas = Pessoa.objects.filter(nome__icontains=q)[:10]
    resultados = []
    
    for p in pessoas:
        email = p.email
        telefone = p.telefone
        
        if p.user:
            if not email:
                email = p.user.email
            if not telefone and hasattr(p.user, 'perfil') and p.user.perfil.telefone:
                telefone = p.user.perfil.telefone
            
        resultados.append({
            'nome': str(p),
            'email': email or '',
            'telefone': telefone or ''
        })
        
    # Também buscar usuários que possam não ter Pessoa criada ainda, apenas como sugestão
    usuarios = User.objects.filter(first_name__icontains=q) | User.objects.filter(username__icontains=q)
    for u in usuarios[:5]:
        nome = f"{u.first_name} {u.last_name}".strip() or u.username
        # Evitar duplicados se já estiver na lista
        if not any(r['nome'] == nome for r in resultados):
            telefone = ''
            if hasattr(u, 'perfil') and u.perfil.telefone:
                telefone = u.perfil.telefone
                
            resultados.append({
                'nome': nome,
                'email': u.email or '',
                'telefone': telefone or ''
            })
            
    return JsonResponse({'pessoas': resultados})
