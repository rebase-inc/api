FROM alpine

WORKDIR /api

EXPOSE 5000

ARG PYPI_SERVER_HOST
ARG PYPI_SERVER_SCHEME
ARG PYPI_SERVER_PORT

RUN apk update && \
    apk add \
        --no-cache \
        ca-certificates \
        gcc \
        libmagic \
        libpq \
        musl-dev \
        openssh-client \
        postgresql-dev \
        gcc \
        python3-dev \
        python3 && \
    pyvenv /venv/web && \
    source /venv/web/bin/activate && \
    pip install \
        --no-cache-dir \
        --upgrade pip

COPY ./requirements.txt /requirements.txt
COPY ./conf/gunicorn.dev.conf /conf/gunicorn.dev.conf 
COPY ./rebase/common/dev.py /settings/dev.py

RUN source /venv/web/bin/activate && \
    pip install \
        --no-cache-dir \
        --trusted-host ${PYPI_SERVER_HOST} \
        --extra-index-url ${PYPI_SERVER_SCHEME}${PYPI_SERVER_HOST}:${PYPI_SERVER_PORT} \
        --requirement /requirements.txt

CMD ["/venv/web/bin/gunicorn", "-c", "conf/gunicorn.dev.conf", "rebase.scripts.wsgi:app"]
