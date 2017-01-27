FROM alpine

RUN apk --quiet update && \
    apk --quiet add \
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
    pip --quiet install \
        --no-cache-dir \
        --upgrade pip

COPY ./requirements.txt /requirements.txt

ARG PYTHON_COMMONS_HOST
ARG PYTHON_COMMONS_SCHEME
ARG PYTHON_COMMONS_PORT

RUN source /venv/web/bin/activate && \
    pip --quiet install \
        --no-cache-dir \
        --trusted-host ${PYTHON_COMMONS_HOST} \
        --extra-index-url ${PYTHON_COMMONS_SCHEME}${PYTHON_COMMONS_HOST}:${PYTHON_COMMONS_PORT} \
        --requirement /requirements.txt

COPY ./rebase /usr/app/src/rebase
COPY ./conf /usr/app/src/conf

ENV PYTHONPATH "/usr/app/src"

ARG CONFIG

EXPOSE 5000

CMD ["/venv/web/bin/gunicorn",  "-c", "/usr/app/src/conf/gunicorn.dev.conf", "rebase.scripts.wsgi:app"]
