from django.db import models


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
