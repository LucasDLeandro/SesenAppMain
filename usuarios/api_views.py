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
    try:
        contatos_notif = Contato.objects.filter(
            Q(pessoa__nome__icontains=query) |
            Q(pessoa__telefone__icontains=query)
        ).select_related('pessoa')[:10]
        
        for c in contatos_notif:
            if not c.pessoa: continue
            nome_completo = c.pessoa.nome + (f" {c.pessoa.sobrenome}" if c.pessoa.sobrenome else "")
            results.append({
                'id': f"notif_{c.id}",
                'source': 'Diretório de Contatos',
                'nome': nome_completo,
                'email': c.pessoa.email or '',
                'telefone': c.pessoa.telefone or '',
                'cargo': c.role or '',
                'empresa': ''
            })
    except Exception:
        pass

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
        nome = pessoa.nome
        sobrenome = pessoa.sobrenome or ''
        email = pessoa.email or ''
        telefone = pessoa.telefone or ''
        cpf = pessoa.cpf or ''
        
        if getattr(pessoa, 'user', None):
            if not email: email = pessoa.user.email or ''
            if not sobrenome: sobrenome = pessoa.user.last_name or ''
            if not telefone and hasattr(pessoa.user, 'perfil'):
                telefone = getattr(pessoa.user.perfil, 'telefone', '') or ''
                
        if not sobrenome and ' ' in nome:
            parts = nome.split(' ', 1)
            nome = parts[0]
            sobrenome = parts[1]
            
        resultados.append({
            'id': f"pessoa_{pessoa.id}",
            'nome': nome,
            'sobrenome': sobrenome,
            'cpf': cpf,
            'email': email,
            'telefone': telefone,
            'source': 'Pessoa'
        })
        
    # 2. Tentar User
    users = User.objects.filter(Q(first_name__icontains=q) | Q(email__iexact=q) | Q(username__iexact=q))[:5]
    for user in users:
        nome = user.first_name or user.username
        sobrenome = user.last_name or ''
        email = user.email or ''
        telefone = ''
        cpf = ''
        
        if hasattr(user, 'perfil'):
            telefone = getattr(user.perfil, 'telefone', '') or ''
            
        if hasattr(user, 'pessoa_vinculada') and user.pessoa_vinculada:
            pessoa = user.pessoa_vinculada
            if not telefone: telefone = pessoa.telefone or ''
            if not cpf: cpf = pessoa.cpf or ''
            if not sobrenome: sobrenome = pessoa.sobrenome or ''
            if not email: email = pessoa.email or ''
            if not nome: nome = pessoa.nome
            
        if not sobrenome and ' ' in nome:
            parts = nome.split(' ', 1)
            nome = parts[0]
            sobrenome = parts[1]
            
        resultados.append({
            'id': f"user_{user.id}",
            'nome': nome,
            'sobrenome': sobrenome,
            'cpf': cpf,
            'email': email,
            'telefone': telefone,
            'source': 'Usuário'
        })
        
    # 3. Tentar Contato Notificacoes
    try:
        contatos_notif = Contato.objects.filter(Q(pessoa__nome__icontains=q) | Q(pessoa__email__iexact=q) | Q(pessoa__telefone__icontains=q))[:5]
        for contato_notif in contatos_notif:
            pessoa = contato_notif.pessoa
            if not pessoa: continue
            
            nome = pessoa.nome
            sobrenome = pessoa.sobrenome or ''
            email = pessoa.email or ''
            telefone = pessoa.telefone or ''
            cpf = pessoa.cpf or ''
            
            if getattr(pessoa, 'user', None):
                if not email: email = pessoa.user.email or ''
                if not sobrenome: sobrenome = pessoa.user.last_name or ''
            
            if not sobrenome and ' ' in nome:
                parts = nome.split(' ', 1)
                nome = parts[0]
                sobrenome = parts[1]
                
            resultados.append({
                'id': f"notif_{contato_notif.id}",
                'nome': nome,
                'sobrenome': sobrenome,
                'cpf': cpf,
                'email': email,
                'telefone': telefone,
                'source': 'Contato'
            })
    except Exception:
        pass

    return JsonResponse({'resultados': resultados})
