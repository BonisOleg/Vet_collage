#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

if [[ -f courses/data/production_courses.json ]]; then
  python manage.py sync_courses --file courses/data/production_courses.json
fi

if [[ -n "${DJANGO_SUPERUSER_PASSWORD:-}" && -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
  export DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
  if ! python manage.py shell -c "
import os
import sys
from django.contrib.auth import get_user_model
name = os.environ['DJANGO_SUPERUSER_USERNAME']
sys.exit(0 if get_user_model().objects.filter(username=name).exists() else 1)
"; then
    python manage.py createsuperuser --noinput
  fi
fi
