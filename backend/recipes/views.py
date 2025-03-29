from django.shortcuts import redirect

from .models import Recipe


def redirect_to_recipe_detail(request, pk):
    try:
        Recipe.objects.get(pk=pk)
        return redirect(f'/recipes/{pk}/')
    except Recipe.DoesNotExist:
        return redirect('/not-found/')
