#!/bin/sh

echo running entrypoint.sh

# Install requirements (if any)
pip install -r requirements.txt

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Compile messages
django-admin compilemessages

# Run server
python manage.py runserver 0.0.0.0:8000

# Start Gunicorn
# exec gunicorn --workers=1 --bind=0.0.0.0:8000 glik.wsgi:application
