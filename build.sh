#!/usr/bin/env bash
# stop at errors
set -o errexit

# upgrade pip
pip install --upgrade pip

# install dependencies
pip install -r requirements.txt

# collect static files
python manage.py collectstatic --noinput

# run migrations
python manage.py migrate --noinput
