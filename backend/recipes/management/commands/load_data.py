import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Загрузка данных из CSV-файлов'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к CSV-файлу')

    def bulk_create_ingredients(self, model, rows):
        ingredients = []
        for row in rows:
            name, measurement_unit = row[0], row[1]
            existing_ingredient = model.objects.filter(name=name).exists()
            if not existing_ingredient:
                ingredients.append(
                    model(name=name, measurement_unit=measurement_unit)
                )

        model.objects.bulk_create(ingredients)
        return len(ingredients)

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        with open(csv_path, encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

            rows_count = len(rows)
            bulk_count = self.bulk_create_ingredients(Ingredient, rows)

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт ингредиентов завершился успешно! '
                f'Всего {bulk_count} записей было добавлено из {rows_count}.'
            )
        )
