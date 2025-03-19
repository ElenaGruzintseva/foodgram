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
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    search_fields = ('name', 'author')

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
