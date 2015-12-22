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
    . /venv/api && \
    pip install -r /api/requirements.txt
WORKDIR /api
ENV APP_SETTINGS=rebase.common.docker.Dev
EXPOSE 5000
CMD ["bash", "-c", "source /venv/api/bin/activate && python ./manage runserver -h 0.0.0.0 -p 5000"]
