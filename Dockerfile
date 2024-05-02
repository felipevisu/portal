### Build and install packages
FROM python:3.11 as build-python

RUN apt-get -y update \
  && apt-get install -y gettext \
  # Cleanup apt cache
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install poetry==1.8.2
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN --mount=type=cache,mode=0755,target=/root/.cache/pypoetry poetry install

### Final image
FROM python:3.11-slim

RUN groupadd -r portal && useradd -r -g portal portal

RUN apt-get update \
  && apt-get install -y \
  libcairo2 \
  libgdk-pixbuf2.0-0 \
  liblcms2-2 \
  libopenjp2-7 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libssl3 \
  libtiff6 \
  libwebp7 \
  libxml2 \
  libpq5 \
  shared-mime-info \
  mime-support \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN echo 'image/webp webp' >> /etc/mime.types
RUN echo 'image/avif avif' >> /etc/mime.types

RUN mkdir -p /app/media /app/static \
  && chown -R portal:portal /app/

COPY --from=build-python /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=build-python /usr/local/bin/ /usr/local/bin/
COPY . /app
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE "portal.settings"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 8000 to allow communication to/from server
EXPOSE 8000

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["/entrypoint.sh"]

# Start the Django application
CMD ["web"]
