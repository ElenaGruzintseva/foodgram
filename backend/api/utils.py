from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient


def create_update_ingredients(recipe, ingredients_data):
    recipe_ingredients = []

    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data.get('id')
        amount = ingredient_data.get('amount')
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)

        recipe_ingredient = RecipeIngredient(
            recipe=recipe, ingredient=ingredient, amount=amount
        )
        recipe_ingredients.append(recipe_ingredient)

    RecipeIngredient.objects.bulk_create(recipe_ingredients)


def add_favorite_or_shopping_list(request, user, model, serializer_class, pk):
    if not (recipe := Recipe.objects.filter(id=pk).first()):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer = serializer_class(
        data={'user': user.id, 'recipe': recipe.id},
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user, recipe=recipe)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


def remove_favorite_or_shopping_list(user, model, pk):
    recipe = get_object_or_404(Recipe, id=pk)

    recipe_delete = model.objects.filter(user=user, recipe=recipe)
    if not recipe_delete.exists():
        return Response(
            {'ошибка': 'рецепт не найден в избранном или списке покупок'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    recipe_delete.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def generate_shopping_list_pdf(recipes_in_shopping_list):
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'
    ] = "attachment; filename='shopping_list.pdf'"

    p = canvas.Canvas(response)

    pdfmetrics.registerFont(TTFont(
        'AV_Fontimer', './recipes/fonts/AV_Fontimer.ttf'
        ))
    p.setFont('AV_Fontimer', 15)

    p.drawString(100, 800, 'Список покупок:')

    y_position = 780

    for recipe in recipes_in_shopping_list:
        name = recipe['ingredient__name']
        total_amount = recipe['total_amount']
        measurement_unit = recipe['ingredient__measurement_unit']

        item_text = f'{name} ({measurement_unit}) - {total_amount}'
        p.drawString(100, y_position, item_text)

        y_position -= 20

    p.showPage()
    p.save()

    return response
