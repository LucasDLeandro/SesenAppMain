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
    class Meta:
        model = PostoTrabalho
        fields = '__all__'

class ItemCustoExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCustoExtra
        fields = '__all__'

class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = '__all__'

class AlocacaoProfissionalSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.CharField(source='profissional.nome', read_only=True)
    posto_nome = serializers.CharField(source='posto.nome_cargo', read_only=True)
    
    class Meta:
        model = AlocacaoProfissional
        fields = '__all__'
