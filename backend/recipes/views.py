from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from .models import Recipe


def redirect_to_recipe_detail(request, pk):
    if Recipe.objects.filter(pk=pk).exists():
        return redirect(f'/recipes/{pk}/')
    else:
        raise ValidationError(f'Рецепт с id {pk} отсутствует.')
