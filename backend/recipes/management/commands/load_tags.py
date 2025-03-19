import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from pathlib import Path

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Загрузка данных из CSV-файлов'

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
        csv_path = Path(settings.DATA_DIR) / 'tags.csv'

        with open(csv_path, encoding='utf8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

            rows_count = len(rows)
            bulk_count = self.bulk_create_tags(Tag, rows)

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт тэгов завершился успешно! '
                f'Всего {bulk_count} записей было добавлено из {rows_count}.'
            )
        )
