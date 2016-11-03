FROM python:alpine

RUN apk update && \
    apk add \
        bash \
        ca-certificates \
        postgresql-dev \
        gcc \
        python3-dev \
        musl-dev \
        py-virtualenv \
        docker

RUN pyvenv /venv/build && \
    source /venv/build/bin/activate && \
    pip install --upgrade pip && \
    pip install wheel 

VOLUME /wheelhouse

WORKDIR /api

CMD ["bash"]
