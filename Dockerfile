FROM debian
COPY ./requirements.txt /api/requirements.txt
RUN apt-get update && \
    apt-get install -y \
        openssh-client \
        libpq-dev \
        python3.4 \
        python3-pip \
        python-psycopg2
RUN easy_install3 -U pip && \
    pip install virtualenv && \
    virtualenv -p python3 /venv/api && \
    mkdir -p \
    /uploads \
    /root/.ssh && \
    /venv/api/bin/pip install -r /api/requirements.txt
WORKDIR /api
ENV APP_SETTINGS=/api/rebase/common/dev.py
CMD ["/venv/api/bin/gunicorn", "-c", "/api/etc/gunicorn.dev.conf", "wsgi:app"]
