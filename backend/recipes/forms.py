from django import forms
from django.core.exceptions import ValidationError

from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'ingredients',
            'tags',
            'text',
            'image',
            'cooking_time',
        )

    def save(self, commit=True):
        ingredients = self.cleaned_data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент.'
            )

        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
