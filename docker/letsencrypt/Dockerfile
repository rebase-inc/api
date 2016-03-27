FROM alpine

RUN apk add --update \
    augeas-libs \
    build-base \
    git \
    libffi-dev \
    linux-headers \
    openssl-dev \
    python-dev \
    py-psutil \
    py-virtualenv && \
    rm -rf /var/cache/apk/* && \
    git clone https://github.com/letsencrypt/letsencrypt && \
    cd letsencrypt && \
    ./letsencrypt-auto-source/letsencrypt-auto --os-packages-only && \
    ./tools/venv.sh

COPY webroot.ini /config/webroot.ini

ENTRYPOINT ["/letsencrypt/venv/bin/letsencrypt"]

CMD ["--help"]
