import csv
from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка данных из CSV-файлов'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к CSV-файлу')

    def bulk_create_tags(self, model, rows):
        tags = []
        for row in rows:
            name, slug = row[0], row[1]
            existing_tag = model.objects.filter(slug=slug).exists()
            if not existing_tag:
                tags.append(model(name=name, slug=slug))

        model.objects.bulk_create(tags)
        return len(tags)

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        try:
            with open(csv_path, encoding='utf8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

                rows_count = len(rows)
                bulk_count = self.bulk_create_tags(Tag, rows)

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
