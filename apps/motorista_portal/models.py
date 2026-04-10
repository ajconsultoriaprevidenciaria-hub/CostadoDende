from django.db import models
from django.utils import timezone


class ChecklistViagem(models.Model):
    """Checklist obrigatório antes de iniciar viagem."""

    carga = models.ForeignKey(
        'fretes.Carga',
        on_delete=models.CASCADE,
        related_name='checklists',
    )
    motorista = models.ForeignKey(
        'fretes.Motorista',
        on_delete=models.CASCADE,
        related_name='checklists',
    )
    data_hora = models.DateTimeField(default=timezone.now)
    observacoes = models.TextField(blank=True)
    concluido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Checklist de Viagem'
        verbose_name_plural = 'Checklists de Viagem'

    def __str__(self):
        return f'Checklist - {self.carga} ({self.data_hora:%d/%m/%Y %H:%M})'


class ItemChecklist(models.Model):
    """Item individual do checklist com foto obrigatória."""

    CATEGORIA_CHOICES = [
        ('pneus', 'Pneus'),
        ('retrovisores', 'Retrovisores'),
        ('parabrisa', 'Para-brisa'),
        ('tanque', 'Tanque'),
        ('farois', 'Faróis'),
        ('freios', 'Freios'),
        ('documentos', 'Documentos'),
        ('outros', 'Outros'),
    ]

    STATUS_CHOICES = [
        ('ok', 'OK'),
        ('atencao', 'Atenção'),
        ('critico', 'Crítico'),
    ]

    checklist = models.ForeignKey(
        ChecklistViagem,
        on_delete=models.CASCADE,
        related_name='itens',
    )
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ok')
    foto = models.ImageField(upload_to='checklist/%Y/%m/')
    observacao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['categoria']
        verbose_name = 'Item do Checklist'
        verbose_name_plural = 'Itens do Checklist'

    def __str__(self):
        return f'{self.get_categoria_display()} - {self.get_status_display()}'


class DespesaViagem(models.Model):
    """Despesa genérica vinculada a uma carga/viagem."""

    TIPO_CHOICES = [
        ('pedagio', 'Pedágio'),
        ('alimentacao', 'Alimentação'),
        ('manutencao', 'Manutenção'),
        ('hospedagem', 'Hospedagem'),
        ('abastecimento', 'Abastecimento'),
        ('outros', 'Outros'),
    ]

    carga = models.ForeignKey(
        'fretes.Carga',
        on_delete=models.CASCADE,
        related_name='despesas',
    )
    motorista = models.ForeignKey(
        'fretes.Motorista',
        on_delete=models.CASCADE,
        related_name='despesas',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=255, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.now)
    comprovante = models.ImageField(upload_to='despesas/%Y/%m/', blank=True)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Despesa de Viagem'
        verbose_name_plural = 'Despesas de Viagem'

    def __str__(self):
        return f'{self.get_tipo_display()} - R$ {self.valor}'


class AbastecimentoViagem(models.Model):
    """Registro de abastecimento com detalhes do posto e cupom fiscal."""

    despesa = models.OneToOneField(
        DespesaViagem,
        on_delete=models.CASCADE,
        related_name='abastecimento',
    )
    posto = models.CharField(max_length=200)
    litros = models.DecimalField(max_digits=10, decimal_places=2)
    preco_litro = models.DecimalField(max_digits=8, decimal_places=4)
    foto_cupom = models.ImageField(upload_to='abastecimentos/%Y/%m/')

    class Meta:
        verbose_name = 'Abastecimento'
        verbose_name_plural = 'Abastecimentos'

    def __str__(self):
        return f'{self.posto} - {self.litros}L'
