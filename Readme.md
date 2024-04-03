# How to run

### Run in localhost

1. Install the Poetry package manager

```console
sudo apt-get install python3-poetry
```

2. Install the dev dependencies:

```console
poetry install
```

3. Setup a `.env` file accordingly with `.env.example`

4. Run the migrations:

```console
poetry run python manage.py migrate
```

5. Start the server:

```console
poetry run python manage.py runserver
```

### Run with Dockerfile

1. Create a build:

```console
docker build -t portal-backend:latest .
```

2. Run the image using the `.env` file to set the environment variables:

```console
docker run -d -p 8000:8000 --env-file=.env portal-backend:latest
```

Warning: to run the container in localhost with a local database it's necessary to setup
the host as `host.docker.internal` in order to enable docker to access the local resourses.

Example:

```console
DATABASE_URL=postgres://postgres:V@visual582@host.docker.internal:5432/portal
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
docker compose -f .devcontainer/docker-compose.yml build
```

3. Create the containers:

```console
docker compose --env-file .devcontainer/backend.env  -f .devcontainer/docker-compose.yml up -d
```
