from django.db import models
from django.core.validators import RegexValidator

from foodgram.constants import MAX_CHAR_LENGTH, MAX_COLOR_LENGTH
from users.models import User


class Ingredient(models.Model):

    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_CHAR_LENGTH
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField('Название тэга', max_length=MAX_CHAR_LENGTH)
    color = models.CharField('Цвет', max_length=MAX_COLOR_LENGTH)
    slug = models.SlugField(
        'Slug',
        max_length=MAX_CHAR_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    text = models.TextField('Описание')
    name = models.CharField('Название рецепта', max_length=MAX_CHAR_LENGTH)
    image = models.ImageField('Фотография', upload_to='recipes/images/')
    cooking_time = models.IntegerField('Время приготовления')
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.IntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return self.recipe.name
