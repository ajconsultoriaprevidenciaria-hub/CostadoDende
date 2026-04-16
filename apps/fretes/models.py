from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
	criado_em = models.DateTimeField(auto_now_add=True)
	atualizado_em = models.DateTimeField(auto_now=True)
	ativo = models.BooleanField(default=True)

	class Meta:
		abstract = True


class Cliente(BaseModel):
	nome = models.CharField(max_length=150)
	nome_fantasia = models.CharField(max_length=150, blank=True)
	documento = models.CharField(max_length=18, unique=True)
	contato = models.CharField(max_length=120, blank=True)
	telefone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	cidade = models.CharField(max_length=100, blank=True)
	uf = models.CharField(max_length=2, blank=True)

	class Meta:
		ordering = ['nome']
		verbose_name = 'Cliente'
		verbose_name_plural = 'Clientes'

	def __str__(self):
		return self.nome


class Motorista(BaseModel):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='motorista',
	)
	nome = models.CharField(max_length=150)
	cpf = models.CharField(max_length=14, unique=True)
	cnh = models.CharField(max_length=20, unique=True)
	telefone = models.CharField(max_length=20, blank=True)

	class Meta:
		ordering = ['nome']
		verbose_name = 'Motorista'
		verbose_name_plural = 'Motoristas'

	def __str__(self):
		return self.nome


class LocalCarregamento(BaseModel):
	nome = models.CharField(max_length=150)
	cidade = models.CharField(max_length=100)
	uf = models.CharField(max_length=2)
	endereco = models.CharField(max_length=255, blank=True)

	class Meta:
		ordering = ['nome']
		verbose_name = 'Local de carregamento'
		verbose_name_plural = 'Locais de carregamento'

	def __str__(self):
		return f'{self.nome} - {self.cidade}/{self.uf}'


class Caminhao(BaseModel):
	placa = models.CharField(max_length=8, unique=True)
	motorista_principal = models.ForeignKey(
		Motorista,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='caminhoes',
	)
	local_carregamento = models.ForeignKey(
		LocalCarregamento,
		on_delete=models.PROTECT,
		related_name='caminhoes',
	)
	observacoes = models.TextField(blank=True)

	class Meta:
		ordering = ['placa']
		verbose_name = 'Caminhão'
		verbose_name_plural = 'Caminhões'

	def __str__(self):
		return self.placa

	@property
	def numero_compartimentos(self):
		return self.compartimentos.count()

	@property
	def capacidade_total_litros(self):
		total = self.compartimentos.aggregate(total=models.Sum('capacidade_litros'))['total']
		return total or Decimal('0.00')


class CaminhaoDocumento(BaseModel):
	TIPO_DOCUMENTO = [
		('crlv', 'CRLV'),
		('licenca_ambiental', 'Licença Ambiental'),
		('antt', 'ANTT'),
		('contrato_social', 'Contrato Social da Transportadora'),
		('civ', 'CIV'),
		('cipp', 'CIPP'),
		('tacografo', 'Tacógrafo'),
		('outros', 'Outros'),
	]

	caminhao = models.ForeignKey(
		Caminhao,
		on_delete=models.CASCADE,
		related_name='documentos',
	)
	tipo = models.CharField(max_length=32, choices=TIPO_DOCUMENTO)
	descricao = models.CharField(max_length=150, blank=True)
	arquivo = models.FileField(upload_to='documentos_caminhao/%Y/%m/')
	data_validade = models.DateField(null=True, blank=True, verbose_name='Validade')
	observacoes = models.TextField(blank=True)

	class Meta:
		ordering = ['caminhao__placa', 'tipo', 'descricao']
		verbose_name = 'Documento do caminhão'
		verbose_name_plural = 'Documentos do caminhão'

	def __str__(self):
		desc = f' / {self.descricao}' if self.descricao else ''
		return f'{self.caminhao.placa} – {self.get_tipo_display()}{desc}'


class Compartimento(models.Model):
	caminhao = models.ForeignKey(
		Caminhao,
		on_delete=models.CASCADE,
		related_name='compartimentos',
	)
	numero = models.PositiveSmallIntegerField()
	capacidade_litros = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		ordering = ['caminhao__placa', 'numero']
		unique_together = ('caminhao', 'numero')
		verbose_name = 'Compartimento'
		verbose_name_plural = 'Compartimentos'

	def __str__(self):
		return f'{self.caminhao.placa} - Compartimento {self.numero}'


class Produto(BaseModel):
	nome = models.CharField(max_length=120, unique=True)
	descricao = models.CharField(max_length=255, blank=True)

	class Meta:
		ordering = ['nome']
		verbose_name = 'Produto'
		verbose_name_plural = 'Produtos'

	def __str__(self):
		return self.nome


class Fornecedor(BaseModel):
	nome = models.CharField(max_length=150)
	documento = models.CharField(max_length=18, unique=True)
	contato = models.CharField(max_length=120, blank=True)
	telefone = models.CharField(max_length=20, blank=True)
	email = models.EmailField(blank=True)
	cidade = models.CharField(max_length=100, blank=True)
	uf = models.CharField(max_length=2, blank=True)

	class Meta:
		ordering = ['nome']
		verbose_name = 'Fornecedor'
		verbose_name_plural = 'Fornecedores'

	def __str__(self):
		return self.nome


class Rota(BaseModel):
	ORIGEM_CHOICES = [
		('Candeias/BA', 'Candeias - BA'),
		('São Francisco do Conde/BA', 'São Francisco do Conde - BA'),
		('Suape/PE', 'Suape - PE'),
	]

	nome = models.CharField(max_length=150)
	origem = models.CharField(max_length=150, choices=ORIGEM_CHOICES)
	destino = models.CharField(max_length=150)
	destino_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='Latitude destino')
	destino_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name='Longitude destino')
	distancia_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	class Meta:
		ordering = ['nome']
		verbose_name = 'Rota'
		verbose_name_plural = 'Rotas'

	def __str__(self):
		return self.nome


class TabelaFrete(BaseModel):
	cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='tabelas_frete')
	produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='tabelas_frete')
	rota = models.ForeignKey(Rota, on_delete=models.CASCADE, related_name='tabelas_frete')
	valor_por_litro = models.DecimalField(max_digits=10, decimal_places=4)
	vigencia_inicio = models.DateField(default=timezone.localdate)
	vigencia_fim = models.DateField(null=True, blank=True)

	class Meta:
		ordering = ['cliente__nome', 'produto__nome', 'rota__nome', '-vigencia_inicio']
		verbose_name = 'Tabela de frete'
		verbose_name_plural = 'Tabelas de frete'
		constraints = [
			models.UniqueConstraint(
				fields=['cliente', 'produto', 'rota', 'vigencia_inicio'],
				name='unique_tabela_frete_vigencia',
			)
		]

	def __str__(self):
		return f'{self.cliente} - {self.produto} - {self.rota}'

	def clean(self):
		if self.vigencia_fim and self.vigencia_fim < self.vigencia_inicio:
			raise ValidationError('A vigência final não pode ser menor que a inicial.')


class Carga(BaseModel):
	data_carga = models.DateField(default=timezone.localdate)
	cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cargas')
	fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name='cargas')
	produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='cargas', blank=True, null=True)
	caminhao = models.ForeignKey(Caminhao, on_delete=models.PROTECT, related_name='cargas')
	motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT, related_name='cargas')
	rota = models.ForeignKey(Rota, on_delete=models.PROTECT, related_name='cargas')
	litros = models.DecimalField(max_digits=12, decimal_places=2)
	valor_frete_litro = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
	valor_total_frete = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
	numero_documento = models.CharField(max_length=50, blank=True)
	observacoes = models.TextField(blank=True)

	class Meta:
		ordering = ['-data_carga', '-id']
		verbose_name = 'Carga'
		verbose_name_plural = 'Cargas'

	def __str__(self):
		return f'{self.data_carga:%d/%m/%Y} - {self.cliente}'

	def buscar_tabela_frete(self):
		tabelas = TabelaFrete.objects.filter(
			cliente=self.cliente,
			produto=self.produto,
			rota=self.rota,
			vigencia_inicio__lte=self.data_carga,
			ativo=True,
		).filter(
			models.Q(vigencia_fim__isnull=True) | models.Q(vigencia_fim__gte=self.data_carga)
		).order_by('-vigencia_inicio')
		return tabelas.first()

	def clean(self):
		super().clean()
		if self.caminhao_id and self.motorista_id and self.caminhao.motorista_principal_id and self.motorista_id != self.caminhao.motorista_principal_id:
			# permitido, mas deixa explícito que o caminhão pode rodar com outro motorista
			pass

		if self.litros and self.caminhao_id and self.litros > self.caminhao.capacidade_total_litros:
			raise ValidationError({'litros': 'O volume informado excede a capacidade total do caminhão.'})

		if not self.valor_frete_litro:
			if self.cliente_id and self.produto_id and self.rota_id and self.data_carga:
				tabela = self.buscar_tabela_frete()
				if not tabela:
					raise ValidationError(
						'Não existe tabela de frete cadastrada para esta combinação. Informe o valor por litro manualmente.'
					)

	def save(self, *args, **kwargs):
		if not self.valor_frete_litro and self.cliente_id and self.produto_id and self.rota_id and self.data_carga:
			tabela = self.buscar_tabela_frete()
			if tabela:
				self.valor_frete_litro = tabela.valor_por_litro
		if self.litros and self.valor_frete_litro is not None:
			self.valor_total_frete = Decimal(self.litros) * Decimal(self.valor_frete_litro)
		super().save(*args, **kwargs)


class CargaCliente(models.Model):
	carga = models.ForeignKey(Carga, on_delete=models.CASCADE, related_name='clientes_adicionais')
	cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cargas_adicional')
	ordem = models.PositiveSmallIntegerField(default=2)

	class Meta:
		ordering = ['ordem']
		unique_together = ('carga', 'ordem')
		verbose_name = 'Cliente adicional'
		verbose_name_plural = 'Clientes adicionais'

	def __str__(self):
		return f'Cliente {self.ordem:02d} - {self.cliente.nome}'


class CargaCompartimento(models.Model):
	carga = models.ForeignKey(Carga, on_delete=models.CASCADE, related_name='carga_compartimentos')
	compartimento = models.ForeignKey(Compartimento, on_delete=models.CASCADE)
	produto = models.ForeignKey(Produto, on_delete=models.PROTECT)

	class Meta:
		unique_together = ('carga', 'compartimento')
		ordering = ['compartimento__numero']
		verbose_name = 'Compartimento da Carga'
		verbose_name_plural = 'Compartimentos da Carga'

	def __str__(self):
		return f'Boca {self.compartimento.numero} - {self.produto.nome}'
