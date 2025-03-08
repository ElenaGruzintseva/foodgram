from django.db import models

from django.contrib.auth.models import AbstractUser
from foodgram.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=MAX_USERNAME_LENGTH,
        unique=True
    )
    first_name = models.CharField('Имя', max_length=MAX_USERNAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_USERNAME_LENGTH)
    email = models.EmailField(
        'Почтовый адрес', max_length=MAX_EMAIL_LENGTH, unique=True
    )
    avatar = models.ImageField(
        'Аватар', upload_to='users/', null=True, blank=False
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username