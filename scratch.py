
# -*- coding: utf-8 -*-
import os, django
import sys
sys.path.append(r'c:\Lucas\SesenAppMain')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sesen_app.settings')
django.setup()
from django.contrib.auth.models import Group, User
tecnicos = User.objects.filter(groups__name='Telefonia - Técnicos')
print('tecnicos count:', tecnicos.count())

