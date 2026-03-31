from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Adiciona campos extras aqui se quiseres (ex: telefone, foto, etc.)
    # phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Utilizador'
        verbose_name_plural = 'Utilizadores'

    def __str__(self):
        return self.username