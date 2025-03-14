import csv
from django.core.management.base import BaseCommand
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


class Command(BaseCommand):
    help = 'Загрузка данных из CSV-файлов'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к CSV-файлу')

    def bulk_create_recipes(self, model, rows):
        recipes = []
        for row in rows:
            name, text, cooking_time, image, tag_ids, ingredients_data = row

            existing_recipe = model.objects.filter(name=name).exists()
            if existing_recipe:
                continue

            recipe = model.objects.create(
                name=name,
                text=text,
                cooking_time=int(cooking_time),
                image=image,
            )

            tag_ids = [int(tag_id) for tag_id in tag_ids.split(',')]
            tags = Tag.objects.filter(id__in=tag_ids)
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
        csv_path = options['csv_path']

        try:
            with open(csv_path, encoding='utf8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                rows = list(reader)

                rows_count = len(rows)
                bulk_count = self.bulk_create_recipes(Recipe, rows)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Импорт данных завершился успешно! '
                    f'Всего {bulk_count} записей было добавлено из {rows_count}.'
                )
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {csv_path} не найден.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))
