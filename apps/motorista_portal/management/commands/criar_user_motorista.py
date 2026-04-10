"""
Cria um User vinculado a um Motorista existente (para login no portal).
Uso: python manage.py criar_user_motorista <cpf> <senha>
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.fretes.models import Motorista

User = get_user_model()


class Command(BaseCommand):
    help = 'Vincula/cria um User Django para um Motorista (login CPF).'

    def add_arguments(self, parser):
        parser.add_argument('cpf', type=str, help='CPF do motorista (com ou sem máscara)')
        parser.add_argument('senha', type=str, help='Senha de acesso')

    def handle(self, *args, **options):
        cpf = options['cpf'].strip()
        senha = options['senha']

        try:
            motorista = Motorista.objects.get(cpf=cpf)
        except Motorista.DoesNotExist:
            raise CommandError(f'Motorista com CPF "{cpf}" não encontrado.')

        if motorista.user:
            user = motorista.user
            user.set_password(senha)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Senha atualizada para o usuário "{user.username}" (Motorista: {motorista.nome}).'
            ))
        else:
            username = f'mot_{cpf.replace(".", "").replace("-", "")}'
            user = User.objects.create_user(
                username=username,
                password=senha,
                first_name=motorista.nome.split()[0] if motorista.nome else '',
                last_name=' '.join(motorista.nome.split()[1:]) if motorista.nome else '',
            )
            motorista.user = user
            motorista.save()
            self.stdout.write(self.style.SUCCESS(
                f'Usuário "{username}" criado e vinculado ao Motorista "{motorista.nome}".'
            ))
