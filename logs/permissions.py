from rest_framework import permissions

class IsAdminPerfil(permissions.BasePermission):
    """
    Permissão customizada que valida se o usuário possui Perfil e se o tipo é ADMIN.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and 
            request.user.perfil.is_admin
        )
