FROM python:alpine

RUN apk update && \
    apk add \
        ca-certificates \
        postgresql-dev \
        gcc \
        python3-dev \
        musl-dev \
        py-virtualenv

COPY ./requirements.txt /requirements.txt

RUN pyvenv /venv/rq && \
    /venv/rq/bin/pip install --upgrade pip && \
    /venv/rq/bin/pip install -r /requirements.txt

WORKDIR /api

CMD ["/venv/rq/bin/python", "rq-population.py"]
