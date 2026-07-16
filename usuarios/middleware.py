from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AnonymousUser

class JWTCookieMiddleware:
    """
    Middleware que lê o token JWT armazenado em cookies,
    autentica o usuário e protege rotas que não sejam públicas.
    Tenta renovar o token automaticamente se estiver expirado.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Rotas públicas que NÃO precisam de token
        self.public_paths = [
            '/login/',
            '/logout/',
            '/api/token/',
            '/api/token/refresh/',
            '/static/',
            '/media/',
            '/empresas/api/',
        ]

    def __call__(self, request):
        path = request.path_info
        
        # Ignora rotas públicas
        if any(path.startswith(p) for p in self.public_paths):
            return self.get_response(request)

        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        
        # Se não há token, redireciona para login
        if not access_token:
            return redirect(f"{reverse('login')}?next={path}")

        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(access_token)
            user = jwt_auth.get_user(validated_token)
            
            # Se for válido, loga o usuário no request
            request.user = user

            # Intercepta caso exija troca de senha (e não seja a página de logout ou de trocar a própria senha)
            if hasattr(user, 'perfil') and user.perfil.precisa_trocar_senha:
                if not (path.startswith('/trocar-senha/') or path.startswith('/logout/')):
                    return redirect(reverse('trocar_senha'))

        except (InvalidToken, TokenError) as e:
            # Token expirado ou inválido, tenta renovar com o refresh_token
            if refresh_token:
                try:
                    # Tenta usar o refresh_token para obter um novo access_token
                    refresh = RefreshToken(refresh_token)
                    new_access_token = str(refresh.access_token)
                    
                    # Re-valida o novo token
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(new_access_token)
                    user = jwt_auth.get_user(validated_token)
                    request.user = user
                    
                    # Responde normalmente, mas atualiza o cookie do access_token
                    response = self.get_response(request)
                    response.set_cookie(
                        'access_token',
                        new_access_token,
                        httponly=True,
                        samesite='Lax',
                        max_age=60*60*8  # 8 horas (sincronizado com JWT_ACCESS_TOKEN_LIFETIME)
                    )
                    return response
                    
                except (InvalidToken, TokenError):
                    # Refresh token também expirou, redireciona para login
                    return redirect(f"{reverse('login')}?next={path}")
                except Exception as e:
                    # Erro ao renovar, redireciona para login
                    return redirect(f"{reverse('login')}?next={path}")
            else:
                # Sem refresh_token, redireciona para login
                return redirect(f"{reverse('login')}?next={path}")
            
        except Exception as e:
            return redirect(f"{reverse('login')}?next={path}")

        response = self.get_response(request)
        return response
