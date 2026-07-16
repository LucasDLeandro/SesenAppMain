from django.db import models

class StatusEvento(models.TextChoices):
    AGENDADO = 'agendado', 'Agendado'
    ANDAMENTO = 'andamento', 'Em Andamento'
    CONCLUIDO = 'concluido', 'Concluído'
    CANCELADO = 'cancelado', 'Cancelado'

class CategoriaEquipamento(models.TextChoices):
    MICROFONE = 'microfone', 'Microfone'
    MESA_SOM = 'mesa_som', 'Mesa de Som'
    CAIXA_SOM = 'caixa_som', 'Caixa de Som'
    PROJETOR = 'projetor', 'Projetor'
    CABO = 'cabo', 'Cabo / Conector'
    DIVERSOS = 'diversos', 'Diversos'

class StatusEquipamento(models.TextChoices):
    DISPONIVEL = 'disponivel', 'Disponível'
    ALOCADO = 'alocado', 'Alocado em Evento'
    MANUTENCAO = 'manutencao', 'Em Manutenção'
    INATIVO = 'inativo', 'Inativo / Desativado'

class TipoInstalacao(models.TextChoices):
    FIXO = 'fixo', 'Instalação Fixa'
    EVENTOS = 'eventos', 'Uso em Eventos'

class EquipamentoAV(models.Model):
    nome = models.CharField(max_length=200, help_text="Nome do Equipamento (Ex: Microfone Sem Fio Shure)")
    categoria = models.CharField(max_length=50, choices=CategoriaEquipamento.choices, default=CategoriaEquipamento.DIVERSOS)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    patrimonio = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="Número de Patrimônio do TSE")
    
    tipo_instalacao = models.CharField(max_length=20, choices=TipoInstalacao.choices, default=TipoInstalacao.EVENTOS)
    sala_local = models.CharField(max_length=200, blank=True, null=True, help_text="Sala ou Local de Armazenamento/Instalação")
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor do item (R$)")

    status = models.CharField(max_length=20, choices=StatusEquipamento.choices, default=StatusEquipamento.DISPONIVEL)
    observacoes = models.TextField(blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"

class TV(models.Model):
    marca = models.CharField(max_length=100, help_text="Marca da TV")
    modelo = models.CharField(max_length=100, help_text="Modelo da TV")
    tamanho_polegadas = models.IntegerField(help_text="Tamanho em polegadas (ex: 55)")
    patrimonio = models.CharField(max_length=50, unique=True, help_text="Número de Patrimônio do TSE")
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor do item (R$)")
    
    protocolo_sei = models.CharField(max_length=50, blank=True, null=True, help_text="Protocolo SEI do pedido")
    localizacao_atual = models.CharField(max_length=200, blank=True, null=True, help_text="Local onde a TV está atualmente")
    
    status = models.CharField(max_length=20, choices=StatusEquipamento.choices, default=StatusEquipamento.DISPONIVEL)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TV {self.tamanho_polegadas}\" {self.marca} - Pat: {self.patrimonio}"

class TransferenciaTV(models.Model):
    tv = models.ForeignKey(TV, on_delete=models.CASCADE, related_name='transferencias')
    origem = models.CharField(max_length=200, help_text="Local de origem")
    destino = models.CharField(max_length=200, help_text="Local de destino")
    data_transferencia = models.DateTimeField(auto_now_add=True)
    responsavel = models.CharField(max_length=150, help_text="Pessoa/Técnico responsável pela transferência")
    motivo = models.TextField(blank=True, null=True, help_text="Motivo da transferência")

    def __str__(self):
        return f"Transferência TV {self.tv.patrimonio}: {self.origem} -> {self.destino}"

class EventoAV(models.Model):
    nome = models.CharField(max_length=200, help_text="Nome/Título do Evento")
    solicitante = models.CharField(max_length=200, help_text="Área ou pessoa solicitante")
    local = models.CharField(max_length=200, help_text="Local onde será o evento (Ex: Plenário, Auditório I)")
    
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    
    equipamentos_alocados = models.ManyToManyField(
        EquipamentoAV, 
        blank=True, 
        related_name='eventos_alocados',
        help_text="Equipamentos reservados para este evento"
    )
    
    descricao = models.TextField(blank=True, null=True, help_text="Descrição das necessidades de Áudio e Vídeo")
    relatorio_conclusao = models.TextField(blank=True, null=True, help_text="Relatório redigido pelo técnico/supervisor ao concluir o evento")
    status = models.CharField(max_length=20, choices=StatusEvento.choices, default=StatusEvento.AGENDADO)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evento: {self.nome} ({self.data_inicio.strftime('%d/%m/%Y')})"

class StatusOSAV(models.TextChoices):
    ABERTA = 'aberta', 'Aberta'
    ANDAMENTO = 'andamento', 'Em Atendimento'
    CONCLUIDA = 'concluida', 'Concluída'

class OrdemServicoAV(models.Model):
    protocolo = models.CharField(max_length=50, blank=True, null=True, help_text="Protocolo SEI ou Chamado")
    equipamento = models.ForeignKey(EquipamentoAV, on_delete=models.CASCADE, related_name='ordens_servico')
    
    defeito_relatado = models.TextField(help_text="Descrição do problema pelo usuário")
    servico_realizado = models.TextField(blank=True, null=True, help_text="O que foi feito para consertar (Preenchido ao concluir)")
    
    tecnico = models.CharField(max_length=100, blank=True, null=True, help_text="Técnico responsável pelo reparo")
    
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=StatusOSAV.choices, default=StatusOSAV.ABERTA)

    def __str__(self):
        prot = self.protocolo or f"OS-{self.id}"
        return f"{prot} - {self.equipamento.nome}"
