#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --noinput
python seed_data.py
python manage.py collectstatic --noinput
