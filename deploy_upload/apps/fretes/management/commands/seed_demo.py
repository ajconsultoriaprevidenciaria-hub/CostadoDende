from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.fretes.models import (
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


class Command(BaseCommand):
    help = 'Cria usuário administrador e dados de demonstração para o sistema de fretes.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        admin, created = user_model.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@costadodende.local',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin.set_password('Admin@123456')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Usuário admin criado com senha temporária: Admin@123456'))
        else:
            self.stdout.write('Usuário admin já existe.')

        local, _ = LocalCarregamento.objects.get_or_create(
            nome='Base Salvador',
            defaults={'cidade': 'Salvador', 'uf': 'BA', 'endereco': 'Terminal Costa do Dendê'},
        )
        motorista1, _ = Motorista.objects.get_or_create(
            cpf='111.111.111-11',
            defaults={'nome': 'José Santos', 'cnh': 'BA1234567', 'telefone': '(71) 99999-1000'},
        )
        motorista2, _ = Motorista.objects.get_or_create(
            cpf='222.222.222-22',
            defaults={'nome': 'Carlos Oliveira', 'cnh': 'BA7654321', 'telefone': '(71) 99999-2000'},
        )
        caminhao1, _ = Caminhao.objects.get_or_create(
            placa='ABC1D23',
            defaults={'motorista_principal': motorista1, 'local_carregamento': local},
        )
        caminhao2, _ = Caminhao.objects.get_or_create(
            placa='EFG4H56',
            defaults={'motorista_principal': motorista2, 'local_carregamento': local},
        )

        for numero, capacidade in enumerate([Decimal('5000.00'), Decimal('5000.00'), Decimal('5000.00')], start=1):
            Compartimento.objects.get_or_create(
                caminhao=caminhao1,
                numero=numero,
                defaults={'capacidade_litros': capacidade},
            )
        for numero, capacidade in enumerate([Decimal('7000.00'), Decimal('7000.00')], start=1):
            Compartimento.objects.get_or_create(
                caminhao=caminhao2,
                numero=numero,
                defaults={'capacidade_litros': capacidade},
            )

        cliente1, _ = Cliente.objects.get_or_create(
            documento='12.345.678/0001-90',
            defaults={'nome': 'Posto Costa Azul', 'cidade': 'Valença', 'uf': 'BA'},
        )
        cliente2, _ = Cliente.objects.get_or_create(
            documento='98.765.432/0001-10',
            defaults={'nome': 'Posto Ilha Bela', 'cidade': 'Ituberá', 'uf': 'BA'},
        )

        fornecedor1, _ = Fornecedor.objects.get_or_create(
            documento='10.000.000/0001-10',
            defaults={'nome': 'Distribuidora Atlântico', 'cidade': 'Salvador', 'uf': 'BA'},
        )
        fornecedor2, _ = Fornecedor.objects.get_or_create(
            documento='20.000.000/0001-20',
            defaults={'nome': 'Fuel Bahia', 'cidade': 'Candeias', 'uf': 'BA'},
        )

        diesel, _ = Produto.objects.get_or_create(nome='Diesel S10')
        gasolina, _ = Produto.objects.get_or_create(nome='Gasolina Comum')

        rota1, _ = Rota.objects.get_or_create(nome='Salvador x Valença', defaults={'origem': 'Salvador', 'destino': 'Valença', 'distancia_km': Decimal('120.00')})
        rota2, _ = Rota.objects.get_or_create(nome='Salvador x Ituberá', defaults={'origem': 'Salvador', 'destino': 'Ituberá', 'distancia_km': Decimal('210.00')})

        for cliente, produto, rota, valor in [
            (cliente1, diesel, rota1, Decimal('0.1800')),
            (cliente1, gasolina, rota1, Decimal('0.2200')),
            (cliente2, diesel, rota2, Decimal('0.2500')),
            (cliente2, gasolina, rota2, Decimal('0.2800')),
        ]:
            TabelaFrete.objects.get_or_create(
                cliente=cliente,
                produto=produto,
                rota=rota,
                vigencia_inicio=timezone.localdate() - timedelta(days=30),
                defaults={'valor_por_litro': valor},
            )

        cargas = [
            {
                'data_carga': timezone.localdate() - timedelta(days=7),
                'cliente': cliente1,
                'fornecedor': fornecedor1,
                'produto': diesel,
                'caminhao': caminhao1,
                'motorista': motorista1,
                'rota': rota1,
                'litros': Decimal('14000.00'),
                'numero_documento': 'NF-1001',
            },
            {
                'data_carga': timezone.localdate() - timedelta(days=5),
                'cliente': cliente2,
                'fornecedor': fornecedor2,
                'produto': gasolina,
                'caminhao': caminhao2,
                'motorista': motorista2,
                'rota': rota2,
                'litros': Decimal('12000.00'),
                'numero_documento': 'NF-1002',
            },
            {
                'data_carga': timezone.localdate() - timedelta(days=2),
                'cliente': cliente1,
                'fornecedor': fornecedor2,
                'produto': gasolina,
                'caminhao': caminhao1,
                'motorista': motorista1,
                'rota': rota1,
                'litros': Decimal('10000.00'),
                'numero_documento': 'NF-1003',
            },
        ]

        for carga_data in cargas:
            Carga.objects.get_or_create(
                numero_documento=carga_data['numero_documento'],
                defaults=carga_data,
            )

        self.stdout.write(self.style.SUCCESS('Dados de demonstração carregados com sucesso.'))
