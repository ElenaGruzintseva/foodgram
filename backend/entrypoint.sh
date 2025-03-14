#!/bin/bash
set -e

until python manage.py check; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - continuing"

python manage.py makemigrations users --no-input
python manage.py makemigrations recipes --no-input
python manage.py migrate --no-input
python manage.py load_tags data/tags.csv
python manage.py load_data data/ingredients.csv
python manage.py create_superuser -u
python manage.py collectstatic --no-input

exec gunicorn -w 2 -b 0.0.0.0:7000 foodgram.wsgi:application --access-logfile - --error-logfile -
