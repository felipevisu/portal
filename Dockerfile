FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE "portal.settings"

# Set the working directory in the container
WORKDIR /usr/src/app

# Install dependencies
ARG REQUIREMENTS=requirements.txt
COPY $REQUIREMENTS ./
RUN pip install -r $REQUIREMENTS
COPY . .

# Expose port 8000 to allow communication to/from server
EXPOSE 8000

# Start the Django application
CMD ["gunicorn", "portal.wsgi:application", "--bind", "0.0.0.0:8000"]
