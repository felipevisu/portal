FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE "portal.settings"

# Set the working directory in the container
WORKDIR /app

# Install dependencies
WORKDIR /app
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install poetry==1.7.0
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN --mount=type=cache,mode=0755,target=/root/.cache/pypoetry poetry install --no-root

# Copy folder
COPY . /app

# Run migrations
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Expose port 8000 to allow communication to/from server
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "portal.wsgi:application", "--bind", "0.0.0.0:8000"]
