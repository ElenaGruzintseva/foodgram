from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    Exists,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    OuterRef,
    PositiveSmallIntegerField,
    QuerySet,
    SlugField,
    TextField,
    UniqueConstraint,
)

from foodgram.constants import (
    MAX_CHAR_LENGTH,
    MAX_COOKING_TIME,
    MAX_RECIPE_LENGTH,
    MAX_TAG_LENGTH,
    MAX_UNIT_LENGTH,
    MAX_AMOUNT,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
)
from users.models import User


class RecipeQuerySet(QuerySet):

    def favorited(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                FavoriteRecipe.objects.filter(
                    recipe=OuterRef('pk'), user=user_id
                )
            )
        )

    def in_shopping_cart(self, user_id):
        return self.annotate(
            is_in_shopping_cart=Exists(
                ShoppingList.objects.filter(
                    recipe=OuterRef('pk'), user=user_id
                )
            )
        )


class Ingredient(Model):

    name = CharField('Название', max_length=MAX_CHAR_LENGTH)
    measurement_unit = CharField(
        'Единица измерения', max_length=MAX_UNIT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_for_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'

    def clean(self):
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()


class Tag(Model):

    name = CharField('Название тэга', max_length=MAX_TAG_LENGTH)
    slug = SlugField('Slug', max_length=MAX_TAG_LENGTH, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(Model):

    name = CharField('Название рецепта', max_length=MAX_RECIPE_LENGTH)
    ingredients = ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = ManyToManyField(Tag, verbose_name='Тэг')
    text = TextField('Описание')
    image = ImageField('Фотография', upload_to='recipes/images/')
    cooking_time = PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        )
    )
    author = ForeignKey(
        User,
        related_name='recipes',
        on_delete=CASCADE,
        verbose_name='Автор',
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )
    objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
        )

    def __str__(self):
        return f'{self.name}. Автор: {self.author.username}'

    def clean(self):
        self.name = self.name.capitalize()
        return super().clean()


class RecipeIngredient(Model):

    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='recipes',
        verbose_name='Рецепт',
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент',
    )
    amount = PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT)
        )
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredient_in_recipe',
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class AbstractShoppingFavoriteRecipe(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        ordering = ('-id',)

    def __str__(self):
        return f'{self.recipe.name} ({self._meta.verbose_name})'


class FavoriteRecipe(AbstractShoppingFavoriteRecipe):

    class Meta(AbstractShoppingFavoriteRecipe.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_favorite_recipe',
            ),
        )


class ShoppingList(AbstractShoppingFavoriteRecipe):

    class Meta(AbstractShoppingFavoriteRecipe.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_lists'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_shopping_list',
            ),
        )
