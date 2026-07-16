from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def is_admin_check(user):
    if hasattr(user, 'perfil') and user.perfil.is_admin:
        return True
    raise PermissionDenied("Apenas administradores podem acessar esta página.")

@user_passes_test(is_admin_check)
def logs_list_view(request):
    return render(request, 'setups/logs_list.html')
