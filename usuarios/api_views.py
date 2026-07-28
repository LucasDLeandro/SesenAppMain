from django.http import JsonResponse
from django.contrib.auth.models import User
from empresas.models import ContatoEmpresa
from notificacoes.models.contato_notificacao import Contato
from django.db.models import Q

def global_contacts_search_api(request):
    """
    API endpoint to search across User, ContatoEmpresa, and Contato models.
    URL param: ?q=search_term
    Returns: JSON list of matches.
    """
    query = request.GET.get('q', '').strip()
    
    results = []
    
    if len(query) < 2:
        return JsonResponse({'results': []})

    # 1. Search Users
    users = User.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) | 
        Q(email__icontains=query) |
        Q(username__icontains=query)
    )[:10]
    
    for u in users:
        nome_completo = f"{u.first_name} {u.last_name}".strip() or u.username
        results.append({
            'id': f"user_{u.id}",
            'source': 'Usuário do Sistema',
            'nome': nome_completo,
            'email': u.email,
            'telefone': '',
            'cargo': 'Usuário',
            'empresa': 'Sesen'
        })

    # 2. Search Contatos Empresa
    try:
        contatos_empresa = ContatoEmpresa.objects.filter(
            Q(pessoa__nome__icontains=query) |
            Q(pessoa__email__icontains=query) |
            Q(pessoa__telefone__icontains=query)
        ).select_related('empresa', 'pessoa')[:10]
        
        for c in contatos_empresa:
            results.append({
                'id': f"emp_{c.id}",
                'source': 'Contato de Empresa',
                'nome': c.pessoa.nome + (f" {c.pessoa.sobrenome}" if c.pessoa.sobrenome else ""),
                'email': c.pessoa.email or '',
                'telefone': c.pessoa.telefone or '',
                'cargo': c.cargo or '',
                'empresa': c.empresa.nome_empresa if c.empresa else ''
            })
    except Exception:
        pass

    # 3. Search Contatos Notificacoes
    contatos_notif = Contato.objects.filter(
        Q(nome__icontains=query) |
        Q(telefone__icontains=query)
    )[:10]
    
    for c in contatos_notif:
        results.append({
            'id': f"notif_{c.id}",
            'source': 'Diretório de Contatos',
            'nome': c.nome,
            'email': '',
            'telefone': c.telefone or '',
            'cargo': c.role or '',
            'empresa': ''
        })

    # Format for Select2
    # Select2 expects { id: ..., text: ... } or we can format it in JS.
    # Let's provide a 'text' field for easy integration
    for r in results:
        details = [d for d in [r['cargo'], r['empresa']] if d]
        detail_str = f" - {', '.join(details)}" if details else ""
        r['text'] = f"{r['nome']} ({r['source']}){detail_str}"

    return JsonResponse({'results': results})

from .models import Pessoa

def buscar_dados_pessoa_api(request):
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 3:
        return JsonResponse({'resultados': []})
    
    resultados = []
    
    # 1. Tentar Pessoa
    pessoas = Pessoa.objects.filter(Q(cpf=q) | Q(nome__icontains=q) | Q(email__iexact=q))[:5]
    for pessoa in pessoas:
        resultados.append({
            'id': f"pessoa_{pessoa.id}",
            'nome': pessoa.nome,
            'sobrenome': pessoa.sobrenome or '',
            'cpf': pessoa.cpf or '',
            'email': pessoa.email or '',
            'telefone': pessoa.telefone or '',
            'source': 'Pessoa'
        })
        
    # 2. Tentar User
    users = User.objects.filter(Q(first_name__icontains=q) | Q(email__iexact=q) | Q(username__iexact=q))[:5]
    for user in users:
        telefone = ''
        try:
            if hasattr(user, 'perfil'):
                telefone = user.perfil.telefone or ''
        except Exception:
            pass
            
        resultados.append({
            'id': f"user_{user.id}",
            'nome': user.first_name or user.username,
            'sobrenome': user.last_name or '',
            'cpf': '',
            'email': user.email or '',
            'telefone': telefone,
            'source': 'Usuário'
        })
        
    # 3. Tentar Contato Notificacoes
    try:
        contatos_notif = Contato.objects.filter(Q(nome__icontains=q) | Q(email__iexact=q) | Q(telefone__icontains=q))[:5]
        for contato_notif in contatos_notif:
            parts = contato_notif.nome.split(' ', 1)
            nome = parts[0]
            sobrenome = parts[1] if len(parts) > 1 else ''
            resultados.append({
                'id': f"notif_{contato_notif.id}",
                'nome': nome,
                'sobrenome': sobrenome,
                'cpf': '',
                'email': contato_notif.email or '',
                'telefone': contato_notif.telefone or '',
                'source': 'Contato'
            })
    except Exception:
        pass

    return JsonResponse({'resultados': resultados})
