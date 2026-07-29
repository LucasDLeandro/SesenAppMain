import zeep
from zeep import Client
from datetime import datetime

class SeiClient:
    def __init__(self):
        # TODO: Substituir pelas credenciais e URL reais fornecidas pela TI
        self.wsdl_url = "https://sei.tse.jus.br/sei/controlador_ws.php?servico=sei&wsdl"
        self.sigla_sistema = "SESEN"
        self.identificacao_servico = "SEI_API_SESEN"
        
        try:
            self.client = Client(self.wsdl_url)
        except Exception as e:
            self.client = None
            print(f"Erro ao conectar no SEI: {e}")

    def get_processo_info(self, numero_processo):
        """
        Usa o endpoint consultarProcedimento para pegar informações gerais do processo.
        """
        if not self.client:
            return None
            
        try:
            # Estrutura esperada pelo WSDL
            response = self.client.service.consultarProcedimento(
                SiglaSistema=self.sigla_sistema,
                IdentificacaoServico=self.identificacao_servico,
                IdUnidade=None, # Pode ser necessário informar a unidade
                ProtocoloProcedimento=numero_processo,
                SinRetornarAssuntos='S',
                SinRetornarInteressados='N',
                SinRetornarObservacoes='S',
                SinRetornarAndamentoGeracao='N',
                SinRetornarAndamentoConclusao='N',
                SinRetornarUltimoAndamento='N',
                SinRetornarUnidadesProcedimentoAberto='N',
                SinRetornarProcedimentosRelacionados='N',
                SinRetornarProcedimentosAnexados='N'
            )
            return response
        except Exception as e:
            print(f"Erro ao consultar o processo {numero_processo}: {e}")
            return None

    def get_andamentos(self, numero_processo):
        """
        Lista os andamentos do processo, retorna o mais recente.
        """
        if not self.client:
            return []
            
        try:
            # Muitos WSDL do SEI exigem chamar `listarAndamentos`
            # Como a estrutura varia levemente entre tribunais, este é um formato padrão:
            response = self.client.service.listarAndamentos(
                SiglaSistema=self.sigla_sistema,
                IdentificacaoServico=self.identificacao_servico,
                IdUnidade=None,
                ProtocoloProcedimento=numero_processo,
                SinRetornarAtributos='N'
            )
            return response
        except Exception as e:
            print(f"Erro ao listar andamentos do processo {numero_processo}: {e}")
            return []
