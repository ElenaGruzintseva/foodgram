#!/bin/bash
set -e

until python manage.py check; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - continuing"

python manage.py migrate --no-input
python manage.py create_superuser -u
python manage.py load_users
python manage.py load_tags
python manage.py load_ingredients
cp -r /app/media/images* /app/media/recipes/
python manage.py load_recipes
python manage.py collectstatic --no-input

exec gunicorn -w 2 -b 0.0.0.0:8000 foodgram.wsgi:application --access-logfile - --error-logfile -
