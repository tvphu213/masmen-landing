python manage.py makemigrations
python manage.py migrate
python manage.py runserver

## Celery worker
celery -A mysite worker --loglevel=info
