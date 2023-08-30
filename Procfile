web: gunicorn portal.wsgi
celery: python -m celery -A portal worker --loglevel=info
release: python manage.py migrate