from django.contrib import admin

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
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

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

    def favorites_count(self, obj):
        return obj.favorites.count()

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
