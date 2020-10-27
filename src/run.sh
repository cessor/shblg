#!/bin/sh
echo "Compiling messages"
python3 manage.py compilemessages

echo "Making migrations"
python3 manage.py makemigrations

echo "Appling migrations"
python3 manage.py migrate

echo "Collecting static assets"
python3 manage.py collectstatic --no-input

echo "Firing up webserver"
gunicorn psi.wsgi:application --bind 0.0.0.0:8000 --error-logfile '-' --access-logfile '-'

exit 0
