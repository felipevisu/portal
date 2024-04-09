### Build and install packages
FROM python:3.11-slim

RUN apt-get -y update \
  && apt-get install -y \
  gettext \
  libpq5 \
  # Cleanup apt cache
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install poetry==1.7.0
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN --mount=type=cache,mode=0755,target=/root/.cache/pypoetry poetry install --no-root

RUN groupadd -r portal && useradd -r -g portal portal

RUN mkdir -p /app/media /app/static \
  && chown -R portal:portal /app/

COPY . /app

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE "portal.settings"

# Expose port 8000 to allow communication to/from server
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "portal.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
