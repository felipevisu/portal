# How to run

### Run in localhost

1. Create a virtual environment with python:

```console
virtualenv -v venv
```

2. Install the dev dependencies:

```console
pip install -r requirements-dev.txt
```

3. Setup a `.env` file accordingly with `.env.example`

4. Run the migrations:

```console
python manage.py migrate
```

5. Start the server:

```console
python manage.py runserver
```

### Run with Dockerfile

1. Create a build:

```console
docker build -t portal-backend:latest .
```

2. You can optionaly run the docker with localhost setup passing the `requirements-dev.txt` as argument to the buuild:

```console
docker build --build-arg REQUIREMENTS=requirements-dev.txt -t portal-backend-dev .
```

3. Run the image using the `.env` file to set the environment variables:

```console
docker run -d -p 8000:8000 --env-file=.env portal-backend:latest
```

### Run with docker-compose

1. Setup your `.env` file with the docker database and redis:

```
DATABASE_URL=postgres://portal:portal@db:5432/portal
PYTEST_DB_URL=postgres://portal:portal@db:5432/portal-test
CELERY_BROKER_URL=redis://redis:6379/0
REDIS_URL=redis:6379
```

2. Run the build:

```console
docker compose -f .devcontainer/docker-compose.yml up -d --build
```
