FROM python:alpine

COPY ./requirements.txt /requirements.txt

COPY ./requirements_p2.txt /requirements_p2.txt

RUN apk update && \
    apk add \
        postgresql-dev \
        gcc \
        python3-dev \
        musl-dev \
        ca-certificates \
        git \
        py-virtualenv

RUN pyvenv /venv/rq && \
    /venv/rq/bin/pip install --upgrade pip && \
    /venv/rq/bin/pip install -r /requirements.txt && \
    virtualenv /venv/rq_p2 && \
    /venv/rq_p2/bin/pip install --upgrade pip && \
    /venv/rq_p2/bin/pip install -r /requirements_p2.txt

WORKDIR /api

CMD ["/venv/rq/bin/python", "run-worker.py"]
