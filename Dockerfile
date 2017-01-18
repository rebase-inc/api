FROM alpine

EXPOSE 5000

ARG PYTHON_COMMONS_HOST
ARG PYTHON_COMMONS_SCHEME
ARG PYTHON_COMMONS_PORT

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
COPY ./conf/gunicorn.dev.conf /conf/gunicorn.dev.conf 
COPY ./conf/gunicorn.pro.conf /conf/gunicorn.pro.conf 
COPY ./rebase/common/dev.py /settings/dev.py
COPY ./rebase/common/pro.py /settings/pro.py

RUN source /venv/web/bin/activate && \
    pip --quiet install \
        --no-cache-dir \
        --trusted-host ${PYTHON_COMMONS_HOST} \
        --extra-index-url ${PYTHON_COMMONS_SCHEME}${PYTHON_COMMONS_HOST}:${PYTHON_COMMONS_PORT} \
        --requirement /requirements.txt

CMD /venv/web/bin/gunicorn -c $CONFIG rebase.scripts.wsgi:app
