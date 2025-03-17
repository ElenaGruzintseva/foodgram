import csv
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка пользователей из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к CSV-файлу')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        with open(csv_path, encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                username = row['username']
                email = row['email']
                first_name = row['first_name']
                last_name = row['last_name']
                password = row['password']
                is_staff = row['is_staff'].lower() == 'true'
                is_superuser = row['is_superuser'].lower() == 'true'

                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=password,
                        is_staff=is_staff,
                        is_superuser=is_superuser
                    )

        self.stdout.write(
            self.style.SUCCESS('Пользователи успешно загружены!')
        )
