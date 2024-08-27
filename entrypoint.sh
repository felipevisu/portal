#!/bin/bash

# This script will be the entrypoint for the Docker container.
# It checks the first command-line argument and starts the appropriate process.

set -e

if [ "$1" = 'web' ]; then
    # Start the Django web server
    echo "Starting Django web server..."
    exec gunicorn portal.wsgi:application --bind 0.0.0.0:8000 --workers 4
elif [ "$1" = 'celery' ]; then
    # Start the Celery worker
    echo "Starting Celery worker..."
    exec celery -A portal worker -l info
elif [ "$1" = 'beat' ]; then
    # Start the Celery beat
    echo "Starting Celery beat..."
    exec celery -A portal beat -l info
else
    # Default action or custom command
    exec "$@"
fi
