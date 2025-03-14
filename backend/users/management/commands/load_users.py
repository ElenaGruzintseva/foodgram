import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка пользователей из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к CSV-файлу')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        try:
            with open(csv_path, encoding='utf8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    username = row['username']
                    email = row['email']
                    password = row['password']
                    is_staff = row['is_staff'].lower() == 'true'
                    is_superuser = row['is_superuser'].lower() == 'true'

                    if not User.objects.filter(username=username).exists():
                        User.objects.create_user(
                            username=username,
                            email=email,
                            password=password,
                            is_staff=is_staff,
                            is_superuser=is_superuser
                        )

            self.stdout.write(self.style.SUCCESS('Пользователи успешно загружены!'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {csv_path} не найден.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))
