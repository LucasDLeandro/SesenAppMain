import zeep
from zeep.wsse.username import UsernameToken
from decimal import Decimal
import datetime
import logging

logger = logging.getLogger(__name__)

class SiafiClient:
    def __init__(self, wsdl_url=None, ug=None, username=None, password=None):
        # Default Homologação WSDL for testing
        self.wsdl_url = wsdl_url or "https://homextservicos-siafi.tesouro.gov.br/siafi2025he/services/orcamentario/manterOrcamentario?wsdl"
        self.ug = ug or "UG_AQUI"
        self.username = username or "CPF_AQUI"
        self.password = password or "SENHA_AQUI"
        
        # Zeep client setup with WS-Security UsernameToken
        # NOTE: mTLS certificate must be configured in the Session for production.
        try:
            self.client = zeep.Client(
                self.wsdl_url,
                wsse=UsernameToken(self.username, self.password)
            )
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente SIAFI: {e}")
            self.client = None

    def detalhar_empenho(self, numero_ne):
        """
        Consulta o serviço Detalhar Empenho para obter os valores atualizados.
        Retorna um dicionário com os dados extraídos.
        """
        if not self.client:
            return {"sucesso": False, "erro": "Cliente SIAFI não inicializado."}

        try:
            # Estrutura do cabeçalho SIAFI (simplificada baseada na doc, requer adaptação se necessário)
            # ug, sistema, nonce (se alterar base)
            cabecalho_siafi = {
                'ug': self.ug,
                'sistema': 'SesenApp',
            }

            # Enviar a requisição (A documentação não mostra exatamente o nome do método no zeep,
            # então assumimos 'detalharEmpenho' ou similar. O nome exato depende do WSDL).
            # Para testes, podemos retornar um mock caso o WSDL falhe sem certificado mTLS.
            
            # mock for testing purposes (remova e descomente a chamada real em Produção)
            # response = self.client.service.detalharEmpenho(numero_ne, _soapheaders={'cabecalhoSIAFI': cabecalho_siafi})
            
            # SIMULANDO RESPOSTA DA API PARA DESENVOLVIMENTO
            return {
                "sucesso": True,
                "numero_ne": numero_ne,
                "valor_original": Decimal("10000.00"),
                "valor_atual": Decimal("9500.00"), # Houve uma anulação de 500
                "valor_anulado": Decimal("500.00"),
                "data_emissao": datetime.date.today(),
                "status": "ATIVO" 
            }

        except Exception as e:
            logger.error(f"Erro ao detalhar empenho {numero_ne}: {e}")
            return {"sucesso": False, "erro": str(e)}
