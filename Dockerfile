FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

ARG REQUIREMENTS=requirements.txt

WORKDIR /usr/src/app
COPY $REQUIREMENTS ./
RUN pip install -r $REQUIREMENTS
COPY . .

EXPOSE 8000
CMD ["gunicorn", "portal.wsgi.application", "--bind", "0.0.0.0:8000"]