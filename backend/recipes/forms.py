from django import forms
from django.core.exceptions import ValidationError

from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = (
            'name',
            'ingredients',
            'tags',
            'text',
            'image',
            'cooking_time',
        )

    def clean(self):
        cleaned_data = super().clean()

        ingredients = cleaned_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Рецепт должен содержать хотя бы один ингредиент.')

        return cleaned_data
