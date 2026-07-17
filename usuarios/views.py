from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken

@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        # Se já estiver logado via cookie
        if request.COOKIES.get('access_token'):
            return redirect('/')
        return render(request, 'usuarios/login.html')

    elif request.method == 'POST':
        # A API pode retornar JSON para que o JS lide, ou podemos fazer POST normal.
        # Vamos fazer via Fetch (JSON) no frontend
        import json
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except:
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Login na sessão nativa do Django também (útil para admin/rotas legadas)
            django_login(request, user)
            
            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Responder com sucesso e instruir o browser a salvar o cookie (se for API/AJAX)
            # Mas como o Django vai gerenciar os cookies de segurança (HttpOnly):
            response = JsonResponse({'success': True, 'redirect_url': '/'})
            
            # Seta o cookie HttpOnly
            response.set_cookie(
                'access_token', 
                access_token, 
                httponly=True, 
                samesite='Lax',
                max_age=60*60*8  # 8 horas
            )
            response.set_cookie(
                'refresh_token', 
                str(refresh), 
                httponly=True, 
                samesite='Lax',
                max_age=60*60*24*7  # 7 dias
            )
            return response
        else:
            return JsonResponse({'success': False, 'error': 'Credenciais inválidas'}, status=401)

def logout_view(request):
    django_logout(request)
    response = redirect(reverse('login'))
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

@csrf_exempt
def trocar_senha_view(request):
    # Essa rota será acessada pelo JWTCookieMiddleware ou pelo usuário autenticado
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'GET':
        return render(request, 'usuarios/trocar_senha.html')
    
    elif request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            senha_atual = data.get('senha_atual')
            nova_senha = data.get('nova_senha')
            confirma_senha = data.get('confirma_senha')
        except:
            return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)

        # Validar
        if nova_senha != confirma_senha:
            return JsonResponse({'success': False, 'error': 'A nova senha e a confirmação não conferem.'}, status=400)
            
        if not request.user.check_password(senha_atual):
            return JsonResponse({'success': False, 'error': 'Senha atual incorreta.'}, status=400)
            
        if len(nova_senha) < 6:
            return JsonResponse({'success': False, 'error': 'A nova senha deve ter pelo menos 6 caracteres.'}, status=400)

        # Alterar senha
        request.user.set_password(nova_senha)
        request.user.save()
        
        # Atualizar Perfil
        if hasattr(request.user, 'perfil'):
            request.user.perfil.precisa_trocar_senha = False
            request.user.perfil.save()
            
        return JsonResponse({'success': True, 'redirect_url': '/'})

from adm_setup.models import ConfiguracaoGeral
from django.contrib import messages

def gestao_usuarios(request):
    # Pode adicionar restrição para apenas superusers ou staff
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')
        
    config = ConfiguracaoGeral.get_instance()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_global':
            config.notificar_novos_usuarios = request.POST.get('notificar_novos_usuarios') == 'on'
            config.save()
            messages.success(request, 'Configurações de Notificação atualizadas com sucesso!')
            
        elif action == 'save_template':
            config.mensagem_boas_vindas = request.POST.get('mensagem_boas_vindas')
            config.save()
            messages.success(request, 'Template de Boas-Vindas atualizado com sucesso!')
            
        return redirect('gestao_usuarios')
        
    from django.conf import settings
    return render(request, 'usuarios/gestao_usuarios.html', {
        'config': config,
        'default_password': settings.DEFAULT_USER_PASSWORD
    })

def meu_perfil_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'usuarios/meu_perfil.html')
