FROM python:alpine
COPY ./requirements.txt /api/requirements.txt
COPY ./requirements_p2.txt /api/requirements_p2.txt
WORKDIR /api
RUN apk update && \
    apk add postgresql-dev gcc python3-dev musl-dev ca-certificates
RUN pyvenv /venv/api && \
    /venv/api/bin/pip install --upgrade pip && \
    /venv/api/bin/pip install -r requirements.txt && \
    pyvenv /venv/api_p2 && \
    /venv/api_p2/bin/pip install --upgrade pip && \
    /venv/api_p2/bin/pip install -r requirements_p2.txt
ENTRYPOINT ["/venv/api/bin/python", "run-worker.py"]
