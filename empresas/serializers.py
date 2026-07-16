from rest_framework import serializers
from .models import Empresa, ContatoEmpresa

class ContatoEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContatoEmpresa
        fields = '__all__'

class EmpresaSerializer(serializers.ModelSerializer):
    contatos = ContatoEmpresaSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = '__all__'
