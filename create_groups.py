import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()

from django.contrib.auth.models import Group

Group.objects.get_or_create(name='Telefonia - Técnicos')
Group.objects.get_or_create(name='Áudio e Vídeo - Técnicos')
Group.objects.get_or_create(name='Elevadores - Técnicos')
Group.objects.get_or_create(name='Patrimônio - Técnicos')
Group.objects.get_or_create(name='Administrativo')

print('Grupos criados com sucesso!')
