FROM python:3.7

RUN apt-get update && apt-get install -y gcc musl-dev python3-dev \
                              libffi-dev libxslt-dev postgresql

COPY requirements.txt /
RUN pip install -r /requirements.txt

WORKDIR /code
COPY . .
