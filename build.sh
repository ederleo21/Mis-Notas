#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Comando estándar para crear las tablas en una base de datos limpia
python manage.py migrate
