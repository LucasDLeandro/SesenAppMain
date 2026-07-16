from django.db import models

class PadraoSenhaTelefonia(models.Model):
    nome = models.CharField(
        max_length=100,
        default="Template Padrão",
        verbose_name="Nome do Template"
    )
    cabecalho_logo = models.CharField(
        max_length=50, 
        default="TSE", 
        verbose_name="Logo (Texto grande)"
    )
    cabecalho_sublogo = models.CharField(
        max_length=150, 
        default="Tribunal Superior Eleitoral", 
        verbose_name="Sub-logo (Texto menor abaixo da logo)"
    )
    cabecalho_subtitulo = models.CharField(
        max_length=200, 
        default="Secretaria de Administração | COSEN - SESEN", 
        verbose_name="Subtítulo do Cabeçalho (Lado Direito)"
    )
    instrucoes_celular = models.CharField(
        max_length=255, 
        default='2 → "senha" → número desejado',
        verbose_name="Instruções para Celular"
    )
    instrucoes_interurbanas = models.CharField(
        max_length=255, 
        default='2 → "senha" → 014 → código de área → número desejado',
        verbose_name="Instruções Interurbanas"
    )
    instrucoes_internacionais = models.CharField(
        max_length=255, 
        default='2 → "senha" → 0014 → código do país → código da cidade → número',
        verbose_name="Instruções Internacionais"
    )
    
    termo_obrigatorio = models.TextField(
        default='A não confirmação do recebimento deste documento em até 48h ensejará o cancelamento desta senha. Em caso de mudança de lotação, o usuário deve comunicar imediatamente a SESEN. Na ausência de comunicação ou caso o usuário não seja localizado, a senha será cancelada automaticamente. O símbolo (*), quando houver, faz parte da senha e deve ser digitado.',
        verbose_name="Cláusula: Obrigatório"
    )
    termo_ligacoes_longa_distancia = models.TextField(
        default='Ligações de Longa Distância Nacional (DDD) e Internacional (DDI) devem ser realizadas estritamente pelos códigos 014 (Contrato da Claro S.A). O “relatório por ramal” deverá ser atestado pelo próprio servidor em folha própria, enviada pela SESEN, devendo constar o respectivo ramal designado. No caso de terceirizados e estagiários, o atesto deverá ser realizado em conjunto com a chefia imediata, que também assume o atesto em caso de férias do usuário.',
        verbose_name="Cláusula: Ligações de Longa Distância"
    )
    termo_ressarcimento = models.TextField(
        default='As ligações de uso particular e a utilização de serviços não previstos em contratos do TSE deverão ser obrigatoriamente ressarcidas à União por meio de emissão de GRU. O comprovante de pagamento e o atesto deverão ser entregues à SESEN até a data de vencimento estipulada. Dúvidas adicionais: ligue para 8223.',
        verbose_name="Cláusula: Ressarcimento"
    )
    
    ativo = models.BooleanField(
        default=True, 
        help_text="Apenas o padrão marcado como ATIVO será exibido na geração dos PDFs de senha."
    )

    class Meta:
        verbose_name = "Padrão de Documento (Senha)"
        verbose_name_plural = "Padrões de Documento (Senhas)"

    def save(self, *args, **kwargs):
        if self.ativo:
            # Se este estiver sendo salvo como ativo, desativa todos os outros
            PadraoSenhaTelefonia.objects.filter(ativo=True).update(ativo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Ativo" if self.ativo else "Inativo"
        return f"Configuração de PDF #{self.id} ({status})"
