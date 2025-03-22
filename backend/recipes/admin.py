from django.contrib import admin
from rest_framework.exceptions import ValidationError

from .forms import RecipeForm
from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)


class RecipeIngredientInline(admin.TabularInline):

    model = RecipeIngredient
    extra = 1

    def clean(self):
        super().clean()

        if not self.cleaned_data:
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.'
            )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    form = RecipeForm
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author', 'favorites_count')
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text', 'image',),
    )
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    search_fields = ('name', 'author__username', 'tags__name')

    def save_model(self, request, obj, form, change):
        if not obj.ingredients.exists():
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.'
            )
        super().save_model(request, obj, form, change)

    def favorites_count(self, obj):
        return obj.favorited_by.count()

    favorites_count.short_description = 'Число добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
