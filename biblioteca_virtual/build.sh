#!/usr/bin/env bash
# Exit on error
set -o errexit

# Comandos a serem executados durante o build
python manage.py collectstatic --no-input
python manage.py migrate