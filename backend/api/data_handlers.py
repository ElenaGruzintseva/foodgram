from io import BytesIO

from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe, RecipeIngredient


def create_update_ingredients(recipe, ingredients_data):
    recipe_ingredients = [
        RecipeIngredient(
            recipe=recipe,
            ingredient_id=ingredient['ingredient'].id,
            amount=ingredient['amount']
        )
        for ingredient in ingredients_data
    ]
    RecipeIngredient.objects.bulk_create(recipe_ingredients)


def add_favorite_or_shopping_list(request, serializer_class, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)

    serializer = serializer_class(
        data={'user': user.id, 'recipe': recipe.id},
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user, recipe=recipe)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


def remove_favorite_or_shopping_list(request, model, pk):
    user = request.user
    recipe = get_object_or_404(Recipe, id=pk)

    deleted_count, _ = model.objects.filter(user=user, recipe=recipe).delete()
    if deleted_count == 0:
        return Response(
            {'ошибка': 'рецепт не найден в избранном или списке покупок'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(status=status.HTTP_204_NO_CONTENT)


def generate_shopping_list_pdf(recipes_in_shopping_list):
    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)

    pdfmetrics.registerFont(TTFont(
        'AV_Fontimer', './recipes/fonts/AV_Fontimer.ttf'
    ))
    p.setFont('AV_Fontimer', 15)

    p.drawString(100, 800, 'Список покупок:')
    y_position = 780

    for recipe in recipes_in_shopping_list:
        name = recipe['ingredient_name']
        total_amount = recipe['total_amount']
        measurement_unit = recipe['measurement_unit']

        item_text = f'{name} ({measurement_unit}) - {total_amount}'
        p.drawString(100, y_position, item_text)
        y_position -= 20

        if y_position < 50:
            p.showPage()
            p.setFont('AV_Fontimer', 15)
            y_position = 780

    p.save()
    buffer.seek(0)
    return buffer
