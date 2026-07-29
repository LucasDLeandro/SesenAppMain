from rest_framework import serializers
from .models.model_contratos import (
    Contratos, 
    ProcessoLicitatorio, 
    MedicaoMensal, 
    Pagamento,
    TramitacaoSEI,
    CronogramaContratacao,
    TermoAditivo,
    PostoTrabalho,
    ItemCustoExtra,
    Profissional,
    AlocacaoProfissional
)
from empresas.models import Empresa

class TramitacaoSEISerializer(serializers.ModelSerializer):
    atualizado_por_nome = serializers.CharField(source='atualizado_por.username', read_only=True)
    tempo_na_unidade = serializers.IntegerField(read_only=True)
    dentro_do_cronograma = serializers.BooleanField(read_only=True)
    contratacao_numero = serializers.CharField(source='contratacao.numero_processo', read_only=True)

    class Meta:
        model = TramitacaoSEI
        fields = '__all__'

class CronogramaContratacaoSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    fase_artefato_display = serializers.CharField(source='get_fase_artefato_display', read_only=True)

    class Meta:
        model = CronogramaContratacao
        fields = '__all__'

class ProcessoLicitatorioSerializer(serializers.ModelSerializer):
    tramitacoes = TramitacaoSEISerializer(many=True, read_only=True)
    cronogramas = CronogramaContratacaoSerializer(many=True, read_only=True)
    fase_display = serializers.CharField(source='get_fase_display', read_only=True)
    status_cronograma = serializers.CharField(read_only=True)

    class Meta:
        model = ProcessoLicitatorio
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome_empresa', read_only=True)
    empresa_cnpj = serializers.CharField(source='empresa.cnpj', read_only=True)
    processo_numero = serializers.CharField(source='processo_licitatorio.numero_processo', read_only=True)

    class Meta:
        model = Contratos
        fields = '__all__'

class PagamentoSerializer(serializers.ModelSerializer):
    competencia = serializers.CharField(source='medicao.competencia', read_only=True)
    contrato_num = serializers.CharField(source='medicao.contrato.num_contrato', read_only=True)
    empresa_nome = serializers.CharField(source='medicao.contrato.empresa.nome_empresa', read_only=True)
    
    class Meta:
        model = Pagamento
        fields = '__all__'

class MedicaoMensalSerializer(serializers.ModelSerializer):
    pagamento = PagamentoSerializer(read_only=True)
    
    class Meta:
        model = MedicaoMensal
        fields = '__all__'

from rest_framework import serializers
from .models.model_contratos import (
    Contratos, 
    ProcessoLicitatorio, 
    MedicaoMensal, 
    Pagamento,
    TramitacaoSEI,
    CronogramaContratacao,
    TermoAditivo,
    PostoTrabalho,
    ItemCustoExtra,
    Profissional,
    AlocacaoProfissional
)
from empresas.models import Empresa

class TramitacaoSEISerializer(serializers.ModelSerializer):
    atualizado_por_nome = serializers.CharField(source='atualizado_por.username', read_only=True)
    tempo_na_unidade = serializers.IntegerField(read_only=True)
    dentro_do_cronograma = serializers.BooleanField(read_only=True)
    contratacao_numero = serializers.CharField(source='contratacao.numero_processo', read_only=True)

    class Meta:
        model = TramitacaoSEI
        fields = '__all__'

class CronogramaContratacaoSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    fase_artefato_display = serializers.CharField(source='get_fase_artefato_display', read_only=True)

    class Meta:
        model = CronogramaContratacao
        fields = '__all__'

class ProcessoLicitatorioSerializer(serializers.ModelSerializer):
    tramitacoes = TramitacaoSEISerializer(many=True, read_only=True)
    cronogramas = CronogramaContratacaoSerializer(many=True, read_only=True)
    fase_display = serializers.CharField(source='get_fase_display', read_only=True)
    status_cronograma = serializers.CharField(read_only=True)

    class Meta:
        model = ProcessoLicitatorio
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.CharField(source='empresa.nome_empresa', read_only=True)
    empresa_cnpj = serializers.CharField(source='empresa.cnpj', read_only=True)
    processo_numero = serializers.CharField(source='processo_licitatorio.numero_processo', read_only=True)

    class Meta:
        model = Contratos
        fields = '__all__'

class PagamentoSerializer(serializers.ModelSerializer):
    competencia = serializers.CharField(source='medicao.competencia', read_only=True)
    contrato_num = serializers.CharField(source='medicao.contrato.num_contrato', read_only=True)
    empresa_nome = serializers.CharField(source='medicao.contrato.empresa.nome_empresa', read_only=True)
    
    class Meta:
        model = Pagamento
        fields = '__all__'

class MedicaoMensalSerializer(serializers.ModelSerializer):
    pagamento = PagamentoSerializer(read_only=True)
    
    class Meta:
        model = MedicaoMensal
        fields = '__all__'

class TermoAditivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermoAditivo
        fields = '__all__'

class PostoTrabalhoSerializer(serializers.ModelSerializer):
    alocados_count = serializers.SerializerMethodField()

    class Meta:
        model = PostoTrabalho
        fields = '__all__'
        
    def get_alocados_count(self, obj):
        # Assumindo que a relação inversa é alocacoes e tem um campo status
        return obj.alocacoes.filter(status='ATIVO').count()

class ItemCustoExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCustoExtra
        fields = '__all__'

from usuarios.models import Pessoa, FormacaoProfissional

class ProfissionalSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(required=False, allow_blank=True)
    sobrenome = serializers.CharField(required=False, allow_blank=True)
    cpf = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    telefone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    formacoes = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, allow_empty=True
    )
    contrato_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Profissional
        fields = ['id', 'pessoa', 'nome', 'sobrenome', 'cpf', 'telefone', 'email', 'formacoes', 'created_at', 'updated_at', 'tecnico_vinculado', 'contrato_id']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.pessoa:
            ret['nome'] = instance.pessoa.nome
            ret['sobrenome'] = instance.pessoa.sobrenome or ''
            ret['cpf'] = instance.pessoa.cpf or ''
            ret['telefone'] = instance.pessoa.telefone or ''
            ret['email'] = instance.pessoa.email or ''
            ret['formacoes'] = [f.titulo for f in instance.pessoa.formacoes.all()]
        return ret

    def create(self, validated_data):
        nome = validated_data.pop('nome', '')
        sobrenome = validated_data.pop('sobrenome', '')
        cpf = validated_data.pop('cpf', None)
        email = validated_data.pop('email', None)
        telefone = validated_data.pop('telefone', None)
        formacoes = validated_data.pop('formacoes', [])
        contrato_id = validated_data.pop('contrato_id', None)
        
        pessoa = None
        if cpf:
            pessoa = Pessoa.objects.filter(cpf=cpf).first()
        if not pessoa and email:
            pessoa = Pessoa.objects.filter(email=email).first()
            
        if pessoa:
            if nome and not pessoa.nome: pessoa.nome = nome
            if sobrenome and not pessoa.sobrenome: pessoa.sobrenome = sobrenome
            if not pessoa.cpf and cpf: pessoa.cpf = cpf
            if not pessoa.email and email: pessoa.email = email
            if not pessoa.telefone and telefone: pessoa.telefone = telefone
            pessoa.save()
        else:
            if nome:
                pessoa = Pessoa.objects.create(
                    nome=nome, sobrenome=sobrenome, cpf=cpf, email=email, telefone=telefone
                )
                
        if pessoa:
            for titulo in formacoes:
                if titulo.strip():
                    FormacaoProfissional.objects.get_or_create(pessoa=pessoa, titulo=titulo.strip())
        
        validated_data['pessoa'] = pessoa
        profissional = super().create(validated_data)
        
        # Sincronização com ContatoEmpresa se contrato_id foi fornecido
        if contrato_id and pessoa:
            from contratos.models import Contrato
            from empresas.models import ContatoEmpresa
            contrato = Contrato.objects.filter(id=contrato_id).first()
            if contrato and contrato.empresa:
                ContatoEmpresa.objects.get_or_create(
                    empresa=contrato.empresa,
                    pessoa=pessoa,
                    defaults={'cargo': 'Alocado via Contrato'}
                )
                
        return profissional

    def update(self, instance, validated_data):
        nome = validated_data.pop('nome', None)
        sobrenome = validated_data.pop('sobrenome', None)
        cpf = validated_data.pop('cpf', None)
        email = validated_data.pop('email', None)
        telefone = validated_data.pop('telefone', None)
        formacoes = validated_data.pop('formacoes', None)

        pessoa = instance.pessoa
        if pessoa:
            if nome is not None: pessoa.nome = nome
            if sobrenome is not None: pessoa.sobrenome = sobrenome
            if cpf is not None: pessoa.cpf = cpf
            if email is not None: pessoa.email = email
            if telefone is not None: pessoa.telefone = telefone
            pessoa.save()
            
            if formacoes is not None:
                pessoa.formacoes.all().delete()
                for titulo in formacoes:
                    if titulo.strip():
                        FormacaoProfissional.objects.create(pessoa=pessoa, titulo=titulo.strip())
        elif nome:
            instance.pessoa = Pessoa.objects.create(
                nome=nome, sobrenome=sobrenome, cpf=cpf, email=email, telefone=telefone
            )
            if formacoes is not None:
                for titulo in formacoes:
                    if titulo.strip():
                        FormacaoProfissional.objects.create(pessoa=instance.pessoa, titulo=titulo.strip())

        return super().update(instance, validated_data)

class AlocacaoProfissionalSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.CharField(source='profissional.pessoa.nome', read_only=True)
    posto_nome = serializers.CharField(source='posto.nome_cargo', read_only=True)
    
    class Meta:
        model = AlocacaoProfissional
        fields = '__all__'
