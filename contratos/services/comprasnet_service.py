import os
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ComprasNetService:
    BASE_URL = "https://contratos.comprasnet.gov.br/api/v1"

    @classmethod
    def get_token(cls):
        # Primeiro, tenta pegar da variável de ambiente diretamente ou através do settings do Django
        token = getattr(settings, 'COMPRASNET_API_TOKEN', os.environ.get('COMPRASNET_API_TOKEN'))
        return token

    @classmethod
    def obter_contratos_ativos_ug(cls, ug_codigo="070001", filtro_objeto="engenharia"):
        """
        Busca os contratos ativos de uma Unidade Gestora específica.
        Filtra os contratos cujo objeto contenha palavras-chave relacionadas à Engenharia/Equipamentos.
        """
        token = cls.get_token()
        
        headers = {
            'Accept': 'application/json'
        }
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
            
        url = f"{cls.BASE_URL}/contrato/ug/{ug_codigo}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                contratos = data if isinstance(data, list) else data.get('data', [])
                
                # Filtragem simples (ativo e por objeto)
                # Na ausência da estrutura exata do JSON, vamos assumir alguns campos comuns 
                # (isso será ajustado quando virmos a resposta real da API)
                contratos_filtrados = []
                for c in contratos:
                    # assumindo que haja 'status', 'vigencia', 'objeto'
                    # Se 'status' ou 'situacao' indicar vigente
                    # Como a API supostamente retorna "contratos ativos", podemos apenas filtrar por palavra-chave
                    objeto = str(c.get('objeto', '')).lower()
                    
                    if not filtro_objeto or filtro_objeto.lower() in objeto or "equipamento" in objeto:
                        contratos_filtrados.append({
                            'id': c.get('id'),
                            'numero': c.get('numero') or c.get('numero_contrato'),
                            'fornecedor': c.get('nome_fornecedor') or c.get('fornecedor'),
                            'objeto': c.get('objeto'),
                            'inicio_vigencia': c.get('data_inicio_vigencia'),
                            'termino_vigencia': c.get('data_termino_vigencia'),
                            'valor_global': c.get('valor_global') or c.get('valor_inicial'),
                        })
                return contratos_filtrados
            else:
                logger.warning(f"Erro na API do Comprasnet: {response.status_code} - {response.text}")
                # Mock para fins de visualização caso dê erro 401 (falta de token real)
                return cls.get_mock_contratos()
                
        except requests.RequestException as e:
            logger.error(f"Erro de conexão com a API do Comprasnet: {e}")
            return cls.get_mock_contratos()

    @classmethod
    def get_mock_contratos(cls):
        """ Retorna dados mockados para testes quando a API não estiver acessível (ex: falta de token) """
        return [
            {
                'id': 101,
                'numero': '01/2024',
                'fornecedor': 'ENGECORP MANUTENÇÃO PREDIAL LTDA',
                'objeto': 'Prestação de serviços de engenharia e manutenção preventiva e corretiva de equipamentos de ar condicionado.',
                'inicio_vigencia': '2024-01-15',
                'termino_vigencia': '2025-01-15',
                'valor_global': 250000.00
            },
            {
                'id': 102,
                'numero': '12/2023',
                'fornecedor': 'ELEVADORES ATLAS SCHINDLER LTDA',
                'objeto': 'Manutenção preventiva e corretiva de elevadores e sistemas de transporte vertical.',
                'inicio_vigencia': '2023-05-10',
                'termino_vigencia': '2024-05-10',
                'valor_global': 185000.50
            },
            {
                'id': 103,
                'numero': '45/2024',
                'fornecedor': 'TECHNO SYS EQUIPAMENTOS S.A.',
                'objeto': 'Aquisição e instalação de equipamentos para subestação de energia.',
                'inicio_vigencia': '2024-03-01',
                'termino_vigencia': '2024-12-31',
                'valor_global': 1500000.00
            }
        ]
