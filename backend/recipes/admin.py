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
    list_display = (
        'name',
        'author',
        'cooking_time',
        'favorite_count',
        'display_tags',
        'display_ingredients',
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text', 'image',),
    )
    list_filter = ('author', 'name', 'tags',)
    filter_horizontal = ('tags',)
    search_fields = ('name', 'author__username', 'tags__name',)
    readonly_fields = ('favorite_count',)

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def display_tags(self, recipe):
        return ', '.join([tag.name for tag in recipe.tags.all()])

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, recipe):
        return ', '.join(
            f'{entry.ingredient.name} '
            f'{entry.amount} ({entry.ingredient.measurement_unit})'
            for entry in recipe.recipes.all()
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):

    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)
