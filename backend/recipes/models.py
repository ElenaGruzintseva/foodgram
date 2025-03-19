from django.core.validators import (
    MinValueValidator,
    RegexValidator,
    ValidationError
)
from django.db import models


from foodgram.constants import (
    MAX_CHAR_LENGTH,
    MAX_RECIPE_LENGTH,
    MAX_TAG_LENGTH,
    MAX_UNIT_LENGTH,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
    TAG_REGEX
)
from users.models import User


class RecipeQuerySet(models.QuerySet):

    def favorited(self, user_id):
        return self.annotate(
            is_favorited=models.Exists(
                FavoriteRecipe.objects.filter(
                    recipe=models.OuterRef('pk'), user=user_id
                )
            )
        )

    def in_shopping_cart(self, user_id):
        return self.annotate(
            is_in_shopping_cart=models.Exists(
                ShoppingList.objects.filter(
                    recipe=models.OuterRef('pk'), user=user_id
                )
            )
        )


class Ingredient(models.Model):

    name = models.CharField('Название', max_length=MAX_CHAR_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_UNIT_LENGTH
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField('Название тэга', max_length=MAX_TAG_LENGTH)
    slug = models.SlugField(
        'Slug',
        max_length=MAX_TAG_LENGTH,
        unique=True,
        validators=[
            RegexValidator(regex=TAG_REGEX, message='Недопустимый символ')
        ],
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    name = models.CharField('Название рецепта', max_length=MAX_RECIPE_LENGTH)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Тэг')
    text = models.TextField('Описание')
    image = models.ImageField('Фотография', upload_to='recipes/images/')
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME)
        ]
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
        editable=False,
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def clean(self):
        if not hasattr(self, 'ingredients') or self.ingredients.count() == 0:
            raise ValidationError(
                'Рецепт должен содержать как минимум один ингредиент'
            )


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
    amount = models.IntegerField(
        'Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return self.recipe.name


class FavoriteRecipe(models.Model):

    user = models.ForeignKey(
        User,
        related_name='favorite_recipes',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorited_by',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_favorite_recipe'
            )
        ]

    def __str__(self):
        return self.recipe.name


class ShoppingList(models.Model):

    user = models.ForeignKey(
        User,
        related_name='shopping_lists',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_shopping_lists',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_shopping_list'
            )
        ]

    def __str__(self):
        return self.recipe.name
