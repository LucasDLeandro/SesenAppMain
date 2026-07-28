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
    contatos_empresa = ContatoEmpresa.objects.filter(
        Q(nome_contato__icontains=query) |
        Q(email__icontains=query) |
        Q(telefone__icontains=query) |
        Q(whatsapp__icontains=query)
    ).select_related('empresa')[:10]
    
    for c in contatos_empresa:
        results.append({
            'id': f"emp_{c.id}",
            'source': 'Contato de Empresa',
            'nome': c.nome_contato,
            'email': c.email or '',
            'telefone': c.whatsapp or c.telefone or '',
            'cargo': c.cargo or '',
            'empresa': c.empresa.nome_empresa if c.empresa else ''
        })

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
        return JsonResponse({'encontrado': False, 'error': 'Busca muito curta'})
    
    # 1. Tentar Pessoa
    pessoa = Pessoa.objects.filter(Q(cpf=q) | Q(nome__icontains=q) | Q(email__iexact=q)).first()
    if pessoa:
        return JsonResponse({
            'encontrado': True,
            'nome': pessoa.nome,
            'sobrenome': pessoa.sobrenome or '',
            'cpf': pessoa.cpf or '',
            'email': pessoa.email or '',
            'telefone': pessoa.telefone or ''
        })
        
    # 2. Tentar ContatoEmpresa
    contato_emp = ContatoEmpresa.objects.filter(Q(nome_contato__icontains=q) | Q(email__iexact=q) | Q(whatsapp__icontains=q)).first()
    if contato_emp:
        parts = contato_emp.nome_contato.split(' ', 1)
        nome = parts[0]
        sobrenome = parts[1] if len(parts) > 1 else ''
        return JsonResponse({
            'encontrado': True,
            'nome': nome,
            'sobrenome': sobrenome,
            'cpf': '',
            'email': contato_emp.email or '',
            'telefone': contato_emp.whatsapp or contato_emp.telefone or ''
        })
        
    # 3. Tentar User
    user = User.objects.filter(Q(first_name__icontains=q) | Q(email__iexact=q) | Q(username__iexact=q)).first()
    if user:
        return JsonResponse({
            'encontrado': True,
            'nome': user.first_name or user.username,
            'sobrenome': user.last_name or '',
            'cpf': '',
            'email': user.email or '',
            'telefone': getattr(user, 'perfil', None) and user.perfil.telefone or ''
        })
        
    # 4. Tentar Contato Notificacoes
    contato_notif = Contato.objects.filter(Q(nome__icontains=q) | Q(email__iexact=q) | Q(telefone__icontains=q)).first()
    if contato_notif:
        parts = contato_notif.nome.split(' ', 1)
        nome = parts[0]
        sobrenome = parts[1] if len(parts) > 1 else ''
        return JsonResponse({
            'encontrado': True,
            'nome': nome,
            'sobrenome': sobrenome,
            'cpf': '',
            'email': contato_notif.email or '',
            'telefone': contato_notif.telefone or ''
        })

    return JsonResponse({'encontrado': False})
