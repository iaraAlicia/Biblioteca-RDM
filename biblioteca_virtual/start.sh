#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Aplicar as migrações do banco de dados (roda toda vez que o app inicia)
python manage.py migrate

# 2. Iniciar o servidor Gunicorn
gunicorn biblioteca_virtual.wsgi:application --bind 0.0.0.0:10000