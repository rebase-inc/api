FROM debian
COPY ./requirements.txt /api/requirements.txt
RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        python3.4 \
        python3-pip \
        python-psycopg2
RUN easy_install3 -U pip && \
    pip install virtualenv && \
    virtualenv -p python3 /venv/api && \
    mkdir /uploads /root/.ssh && \
    /venv/api/bin/pip install -r /api/requirements.txt
WORKDIR /api
ENV APP_SETTINGS=/api/rebase/common/docker.py
EXPOSE 5000
CMD ["/venv/api/bin/python", "./manage", "runserver", "-h", "0.0.0.0", "-p", "5000"]
