from rest_framework import serializers
from .models import Tecnico, SolicitacaoAcesso, LiberacaoAcessoDiaria
from empresas.serializers import EmpresaSerializer

class TecnicoSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome_empresa', read_only=True)
    nome = serializers.CharField(source='pessoa.nome', read_only=True)
    cpf = serializers.CharField(source='pessoa.cpf', read_only=True)
    telefone = serializers.CharField(source='pessoa.telefone', read_only=True)

    class Meta:
        model = Tecnico
        fields = '__all__'

class SolicitacaoAcessoSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome_empresa', read_only=True)
    tecnicos_detalhes = serializers.SerializerMethodField()
    tecnicos_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = SolicitacaoAcesso
        fields = '__all__'
        extra_kwargs = {
            'tecnicos': {'required': False}
        }

    def _process_tecnicos(self, instance, tecnicos_data):
        if tecnicos_data is not None:
            from usuarios.models import Pessoa
            tecnico_objs = []
            for t_data in tecnicos_data:
                # Busca por CPF ou cria
                pessoa, _ = Pessoa.objects.get_or_create(
                    cpf=t_data.get('cpf'),
                    defaults={
                        'nome': t_data.get('nome', ''),
                        'telefone': t_data.get('telefone', '')
                    }
                )
                tecnico, created = Tecnico.objects.get_or_create(
                    pessoa=pessoa,
                    defaults={
                        'rg': t_data.get('rg', ''),
                        'empresa': instance.empresa
                    }
                )
                if not created:
                    # Atualiza os dados
                    pessoa.nome = t_data.get('nome', pessoa.nome)
                    pessoa.telefone = t_data.get('telefone', pessoa.telefone)
                    pessoa.save()
                    tecnico.rg = t_data.get('rg', tecnico.rg)
                    tecnico.empresa = instance.empresa
                    tecnico.save()
                tecnico_objs.append(tecnico)
            instance.tecnicos.set(tecnico_objs)

    def create(self, validated_data):
        tecnicos_data = validated_data.pop('tecnicos_data', None)
        instance = super().create(validated_data)
        self._process_tecnicos(instance, tecnicos_data)
        return instance

    def update(self, instance, validated_data):
        tecnicos_data = validated_data.pop('tecnicos_data', None)
        instance = super().update(instance, validated_data)
        self._process_tecnicos(instance, tecnicos_data)
        return instance

    def get_tecnicos_detalhes(self, obj):
        return [
            {
                'id': t.id,
                'nome': t.nome,
                'cpf': t.cpf,
                'rg': t.rg,
                'telefone': t.telefone
            }
            for t in obj.tecnicos.all()
        ]

class LiberacaoAcessoDiariaSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='solicitacao.empresa.nome_empresa', read_only=True)
    tecnicos_detalhes = serializers.SerializerMethodField()

    class Meta:
        model = LiberacaoAcessoDiaria
        fields = '__all__'

    def get_tecnicos_detalhes(self, obj):
        return [
            {
                'id': t.id,
                'nome': t.nome,
                'cpf': t.cpf,
                'rg': t.rg,
                'telefone': t.telefone
            }
            for t in obj.tecnicos.all()
        ]
