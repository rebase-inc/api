FROM alpine:edge
RUN apk add --update python3 openssh-client file build-base python3-dev postgresql-dev \
    && rm -rf /var/cache/apk/*
COPY ./requirements.txt /api/requirements.txt
RUN pyvenv /venv/api && \
    mkdir -p /uploads /root/.ssh && \
    /venv/api/bin/pip install --upgrade pip && \
    /venv/api/bin/pip install -r /api/requirements.txt
RUN apk del build-base python3-dev postgresql-dev && \
    apk add --update libpq
WORKDIR /api
ENV APP_SETTINGS=/api/rebase/common/dev.py
CMD ["/venv/api/bin/gunicorn", "-c", "/api/etc/gunicorn.dev.conf", "wsgi:app"]
