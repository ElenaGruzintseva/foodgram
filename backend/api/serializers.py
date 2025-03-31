from drf_extra_fields.fields import Base64ImageField
from django.db.models import Count
from djoser.serializers import UserSerializer
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    BooleanField,
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
)
from rest_framework.validators import UniqueTogetherValidator

from .data_handlers import create_update_ingredients
from foodgram.constants import (
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from users.models import Subscribe, User


class RecipeReadSerializer(ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class TagSerializer(ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientGETSerializer(ModelSerializer):

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        model = RecipeIngredient


class RecipeIngredientCreateSerializer(ModelSerializer):

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
    )

    class Meta:
        fields = ('id', 'amount',)
        model = RecipeIngredient


class UserGETSerializer(UserSerializer):

    is_subscribed = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'is_subscribed',
            'avatar',
            *UserSerializer.Meta.fields,
        )

    def get_is_subscribed(self, user):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and user.subscriptions_to.filter(user=request.user).exists()
        )


class RecipeGETSerializer(ModelSerializer):

    author = UserGETSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientGETSerializer(
        many=True, read_only=True, source='recipes'
    )
    is_favorited = BooleanField(read_only=True, default=False)
    is_in_shopping_cart = BooleanField(read_only=True, default=False)

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe


class RecipeCreateSerializer(ModelSerializer):

    image = Base64ImageField(required=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = RecipeIngredientCreateSerializer(many=True, required=True)
    cooking_time = IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
    )

    class Meta:
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe

    def validate(self, obj):
        ingredients = obj.get('ingredients', [])
        tags = obj.get('tags', [])

        if not tags:
            raise ValidationError(
                'Рецепт должен содержать как минимум один тег.'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги не должны повторяться.')

        if not ingredients:
            raise ValidationError(
                'Рецепт должен содержать как минимум один ингредиент.'
            )
        ingredient_ids = {ingredient['id'] for ingredient in ingredients}
        if len(ingredient_ids) != len(ingredients):
            raise ValidationError('Ингредиенты не должны повторяться.')
        return obj

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags_data)

        create_update_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        if ingredients_data is not None:
            instance.ingredients.clear()
            create_update_ingredients(instance, ingredients_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeGETSerializer(instance, context=self.context).data


class BaseFavoriteShoppingSerializer(ModelSerializer):
    class Meta:
        fields = ('recipe', 'user',)
        abstract = True

    def validate(self, obj):
        user = obj['user']
        recipe = obj['recipe']

        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                f'{self.Meta.model._meta.verbose_name} уже существует.'
            )

        return obj

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(BaseFavoriteShoppingSerializer):
    class Meta(BaseFavoriteShoppingSerializer.Meta):
        model = FavoriteRecipe


class ShoppingListSerializer(BaseFavoriteShoppingSerializer):
    class Meta(BaseFavoriteShoppingSerializer.Meta):
        model = ShoppingList


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(UserGETSerializer):

    recipes = SerializerMethodField()
    recipes_count = IntegerField(read_only=True, default=0)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, user):
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = user.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass

        return RecipeReadSerializer(
            recipes, many=True, context=self.context
        ).data


class SubscribeCreateSerializer(ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author',)
        validators = (
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора.',
            ),
        )

    def validate(self, obj):
        user = obj['user']
        author = obj['author']
        if user == author:
            raise ValidationError('Нельзя подписываться на самого себя.')
        return obj

    def to_representation(self, instance):
        author = User.objects.filter(
            id=instance.author.id
        ).annotate(
            recipes_count=Count('recipes')
        ).first()
        return SubscriptionSerializer(
            author, context=self.context
        ).data
