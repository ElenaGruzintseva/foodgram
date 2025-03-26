from drf_extra_fields.fields import Base64ImageField

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
    Tag
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
        validators=(
            MinValueValidator(MIN_AMOUNT),
            MaxValueValidator(MAX_AMOUNT),
        )
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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request and not request.user.is_anonymous:
            user = request.user
            return user.subscriptions_from.filter(author=obj).exists()
        return False


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
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME),
        )
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
                'Рецепт должен содержать как минимум один тэг'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError('Тэги не должны повторяться')

        if not ingredients:
            raise ValidationError(
                'Рецепт должен содержать как минимум один ингредиент'
            )
        ingredients_list = set()
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if amount < MIN_AMOUNT:
                raise ValidationError(
                    f'Количество ингредиента не может быть меньше {MIN_AMOUNT}'
                )
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise ValidationError('Ингредиент не существует')
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Ингредиент уже добавлен в рецепт'
                )
            ingredients_list.add(ingredient_id)

        return obj

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(author=user, **validated_data)

        recipe.tags.set(tags)

        create_update_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance.tags.clear()
        instance.tags.set(tags)

        RecipeIngredient.objects.filter(recipe=instance).delete()

        create_update_ingredients(instance, ingredients_data)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGETSerializer(instance, context=self.context).data


class FavoriteSerializer(ModelSerializer):

    class Meta:
        fields = ('recipe', 'user')
        model = FavoriteRecipe

    def validate(self, obj):
        user = obj['user']

        if user.favorites_recipes.filter(recipe=obj['recipe']).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return obj

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance.recipe, context={'request': request}
        ).data


class ShoppingListSerializer(ModelSerializer):

    class Meta:
        fields = ('recipe', 'user')
        model = ShoppingList

    def validate(self, obj):
        user = obj['user']

        if user.shopping_lists.filter(recipe=obj['recipe']).exists():
            raise ValidationError('Рецепт уже добавлен в корзину')

        return obj

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeReadSerializer(
            instance.recipe, context={'request': request}
        ).data


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscriptionSerializer(UserGETSerializer):

    recipes = SerializerMethodField()
    recipes_count = IntegerField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()

        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                queryset = queryset[:recipes_limit]
            except ValueError:
                pass

        return RecipeReadSerializer(
            queryset, many=True, context={'request': request}
        ).data


class SubscribeCreateSerializer(ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, attrs):
        user = attrs['user']
        author = attrs['author']

        if user == author:
            raise ValidationError('Нельзя подписываться на самого себя.')

        if Subscribe.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')

        return attrs
