from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, correo=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(correo=correo)
            if user.check_password(password):
                return user
            return None
        except Usuario.DoesNotExist:
            return None
