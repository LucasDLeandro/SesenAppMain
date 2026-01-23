from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ELEVATOR_CHOICE = [
    ('1', 'Social 1 - M2674'),
    ('2', 'Social 2 - M2675'),
    ('3', 'Social 3 - M2676'),
    ('4', 'Social 4 - M2677'),
    ('5', 'Social 5 - M2678'),
    ('6', 'Serviço 6 - M2679'),
    ('7', 'Social 7 - M2680'),
    ('8', 'Social 8 - M2681'),
    ('9', 'Social 9 - M2682'),
    ('10', 'Social 10 - M2683'),
    ('11', 'Social 11 - M2684'),
    ('12', 'Social 12 - M2685'),
    ('13', 'Social 13 - M2686'),
    ('14', 'Serviço 14 - M2687'),
]

STATUS_ELEVADOR_CHOICES = [
    ('1', 'Ativo'),
    ('2', 'Parado'),
]

STATUS_OS = [
    (1, 'ABERTA'),
    (2, 'CONCLUIDA'),
]

SERVICES_LIST = [
    ('1', 'Água e Esgoto'),
    ('2', 'Ar Condicionado'),
    ('3', 'Arquitetura e Projetos'),
    ('4', 'Áudio & Vídeo'),
    ('5', 'Carregadores'),
    ('6', 'Copa'),
    ('7', 'Eletrodomésticos e Equip. Eletrônicos'),
    ('8', 'Elevadores'),
    ('9', 'Energia Elétrica'),
    ('10', 'Limpeza'),
    ('11', 'Manutenção Geradores - Corretivas'),
    ('12', 'Manutenção Preditiva'),
    ('13', 'Marcenaria'),
    ('14', 'Obras'),
    ('15', 'Outros Serviços de Manutenção Predial'),
    ('16', 'Serralheria'),
    ('17', 'Obras'),
    ('18', 'Chaveiro'),
    ('19', 'Telefonia'),
]

from .mapa_servicos import Categoria, Servico

from .eng_reg_os_model import EngServiceReg
from .elevadores_reg_os_model import ElevOrderReg
from .elevadores_close_os_model import ElevOrderClose




