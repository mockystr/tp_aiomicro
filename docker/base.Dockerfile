FROM python:3.7

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt /
RUN pip install -r /requirements.txt

ENV POSTGRES_HOST_DB=db
ENV HOST_RABBITMQ=rmq
ENV HOST_ES=es

WORKDIR /code
COPY . .
