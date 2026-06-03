from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ELEVATOR_CHOICE = [
    ('Social 1 - M2674', 'Social 1 - M2674'),
    ('Social 2 - M2675', 'Social 2 - M2675'),
    ('Social 3 - M2676', 'Social 3 - M2676'),
    ('Social 4 - M2677', 'Social 4 - M2677'),
    ('Social 5 - M2678', 'Social 5 - M2678'),
    ('Serviço 6 - M2679', 'Serviço 6 - M2679'),
    ('Privativo 7 - M2680', 'Privativo 7 - M2680'),
    ('Social 8 - M2681', 'Social 8 - M2681'),
    ('Social 9 - M2682', 'Social 9 - M2682'),
    ('Privativo 10 - M2683', 'Privativo 10 - M2683'),
    ('Social 11 - M2684', 'Social 11 - M2684'),
    ('Social 12 - M2685', 'Social 12 - M2685'),
    ('Social 13 - M2686', 'Social 13 - M2686'),
    ('Serviço 14 - M2687', 'Serviço 14 - M2687'),
]



STATUS_ELEVADOR_CHOICES = [
    ('ATIVO', 'ATIVO'),
    ('PARADO', 'PARADO'),
]

STATUS_OS = [
    ('ABERTA', 'ABERTA'),
    ('CONCLUIDA', 'CONCLUIDA'),
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
from .elev_so_model import ElevOrderReg





