from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
	Caminhao,
	Carga,
	Cliente,
	Compartimento,
	Fornecedor,
	LocalCarregamento,
	Motorista,
	Produto,
	Rota,
	TabelaFrete,
)


class CargaModelTest(TestCase):
	def setUp(self):
		self.local = LocalCarregamento.objects.create(nome='Base', cidade='Salvador', uf='BA')
		self.motorista = Motorista.objects.create(nome='Motorista Teste', cpf='000.000.000-00', cnh='123456789')
		self.caminhao = Caminhao.objects.create(
			placa='XYZ1A23',
			motorista_principal=self.motorista,
			local_carregamento=self.local,
		)
		Compartimento.objects.create(caminhao=self.caminhao, numero=1, capacidade_litros=Decimal('5000.00'))
		Compartimento.objects.create(caminhao=self.caminhao, numero=2, capacidade_litros=Decimal('5000.00'))
		self.cliente = Cliente.objects.create(nome='Cliente Teste', documento='11.111.111/0001-11')
		self.fornecedor = Fornecedor.objects.create(nome='Fornecedor Teste', documento='22.222.222/0001-22')
		self.produto = Produto.objects.create(nome='Diesel')
		self.rota = Rota.objects.create(nome='A x B', origem='A', destino='B')
		TabelaFrete.objects.create(
			cliente=self.cliente,
			produto=self.produto,
			rota=self.rota,
			valor_por_litro=Decimal('0.2500'),
		)

	def test_carga_calcula_frete_automaticamente(self):
		carga = Carga.objects.create(
			cliente=self.cliente,
			fornecedor=self.fornecedor,
			produto=self.produto,
			caminhao=self.caminhao,
			motorista=self.motorista,
			rota=self.rota,
			litros=Decimal('8000.00'),
			numero_documento='DOC-1',
		)

		self.assertEqual(carga.valor_frete_litro, Decimal('0.2500'))
		self.assertEqual(carga.valor_total_frete, Decimal('2000.000000'))

	def test_carga_nao_pode_exceder_capacidade(self):
		carga = Carga(
			cliente=self.cliente,
			fornecedor=self.fornecedor,
			produto=self.produto,
			caminhao=self.caminhao,
			motorista=self.motorista,
			rota=self.rota,
			litros=Decimal('12000.00'),
			numero_documento='DOC-2',
		)

		with self.assertRaises(ValidationError):
			carga.clean()
