#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Intentar migrar. Si falla por tablas existentes, sincronizamos el historial.
echo "Sincronizando base de datos en Neon..."
python manage.py migrate --fake-initial || {
    echo "Tablas existentes detectadas. Sincronizando historial de migraciones..."
    python manage.py migrate --fake
}
