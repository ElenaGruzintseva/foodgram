from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, ValidationError

from foodgram.constants import MAX_EMAIL_LENGTH, MAX_USERNAME_LENGTH, REGEX


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    username = models.CharField(
        'Логин',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=(
            RegexValidator(regex=REGEX, message='Недопустимый символ'),
        ),
    )
    first_name = models.CharField('Имя', max_length=MAX_USERNAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_USERNAME_LENGTH)
    email = models.EmailField(
        'Почтовый адрес', max_length=MAX_EMAIL_LENGTH, unique=True
    )
    avatar = models.ImageField(
        'Аватар', upload_to='users/', null=True, blank=True
    )

    class Meta:
        ordering = ('email', 'username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_from',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_to',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_user_author',
            ),
        )

    def __str__(self):
        return f'{self.user.username} подписан(а) на {self.author.username}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')
