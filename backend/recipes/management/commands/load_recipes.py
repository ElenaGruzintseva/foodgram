import csv
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from pathlib import Path

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)


User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка данных из CSV-файлов'

    def bulk_create_recipes(self, model, rows):
        recipes = []
        for row in rows:
            (name, text, cooking_time, image, tags,
             ingredients_data, author_username) = row

            author = User.objects.get(username=author_username)

            existing_recipe = model.objects.filter(name=name).exists()
            if existing_recipe:
                continue

            recipe = model.objects.create(
                name=name,
                text=text,
                cooking_time=int(cooking_time),
                image=image,
                author=author,
            )

            tags = [int(tag_id) for tag_id in tags.split(',')]
            tags = Tag.objects.filter(id__in=tags)
            recipe.tags.set(tags)

            ingredients = []
            for ingredient_data in ingredients_data.split(','):
                ingredient_id, amount = ingredient_data.split('|')
                ingredient = Ingredient.objects.get(id=int(ingredient_id))
                ingredients.append(
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=int(amount)
                    )
                )
            RecipeIngredient.objects.bulk_create(ingredients)

            recipes.append(recipe)

        return len(recipes)

    def handle(self, *args, **options):
        csv_path = Path(settings.DATA_DIR) / 'recipes.csv'

        with open(csv_path, encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            rows = list(reader)

            rows_count = len(rows)
            bulk_count = self.bulk_create_recipes(Recipe, rows)

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт рецептов завершился успешно! '
                f'Всего {bulk_count} записей было добавлено из {rows_count}.'
            )
        )
