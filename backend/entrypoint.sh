#!/bin/bash
set -e

until python manage.py check; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - continuing"

python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py load_data data/ingredients.csv -e
python manage.py create_superuser -u
python manage.py collectstatic --no-input
cp -r /app/collected_static/. /static/static/

exec gunicorn foodgram.wsgi:application --bind 0.0.0.0:7000
