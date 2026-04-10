from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from apps.fretes.models import Motorista

User = get_user_model()


class CPFBackend(ModelBackend):
    """Autenticação via CPF do motorista."""

    def authenticate(self, request, cpf=None, password=None, **kwargs):
        try:
            motorista = Motorista.objects.select_related('user').get(cpf=cpf)
        except Motorista.DoesNotExist:
            return None

        user = motorista.user
        if user is None:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
