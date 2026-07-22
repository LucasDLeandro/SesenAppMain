import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from notificacoes.models.contato_notificacao import Contato

@login_required
@require_POST
def bulk_contatos_view(request):
    """
    Receives a JSON payload with lists of contacts to create, update, and delete.
    Expected payload:
    {
        "create": [{"nome": "...", "telefone": "...", "role": "...", "is_ativo": True}],
        "update": [{"id": 1, "nome": "...", "telefone": "...", "role": "...", "is_ativo": False}],
        "delete": [2, 3] # list of IDs to delete
    }
    """
    try:
        data = json.loads(request.body)
        
        # 1. Delete
        ids_to_delete = data.get('delete', [])
        if ids_to_delete:
            Contato.objects.filter(id__in=ids_to_delete).delete()

        # 2. Update
        updates = data.get('update', [])
        for item in updates:
            c_id = item.get('id')
            if c_id:
                try:
                    contato = Contato.objects.get(id=c_id)
                    contato.nome = item.get('nome', contato.nome)
                    contato.telefone = item.get('telefone', contato.telefone)
                    contato.role = item.get('role', contato.role)
                    # Handle boolean conversion correctly if passed as string 'true'/'false'
                    is_ativo_raw = item.get('is_ativo', contato.is_ativo)
                    contato.is_ativo = is_ativo_raw if isinstance(is_ativo_raw, bool) else (str(is_ativo_raw).lower() == 'true')
                    contato.save()
                except Contato.DoesNotExist:
                    pass

        # 3. Create
        creates = data.get('create', [])
        new_contatos = []
        for item in creates:
            if item.get('nome'): # Basic validation
                is_ativo_raw = item.get('is_ativo', True)
                is_ativo = is_ativo_raw if isinstance(is_ativo_raw, bool) else (str(is_ativo_raw).lower() == 'true')
                new_contatos.append(Contato(
                    nome=item.get('nome'),
                    telefone=item.get('telefone', ''),
                    role=item.get('role', 'Geral'),
                    is_ativo=is_ativo
                ))
                
        if new_contatos:
            Contato.objects.bulk_create(new_contatos)

        return JsonResponse({'status': 'success', 'message': 'Contatos salvos com sucesso!'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON Inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
