FROM python:3.7

COPY requirements.txt /
RUN pip install -r /requirements.txt

ENV HOST_DB=db
ENV HOST_RABBITMQ=rmq
ENV HOST_ES=es

WORKDIR /code
COPY . .
