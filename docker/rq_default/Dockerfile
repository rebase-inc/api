FROM rebase/api
COPY ./requirements_p2.txt /api/requirements_p2.txt
RUN virtualenv -p python2 /venv/api_p2 && \
    /venv/api_p2/bin/pip install --upgrade pip && \
    /venv/api_p2/bin/pip install -r requirements_p2.txt
ENTRYPOINT ["/venv/api/bin/python", "run-worker.py"]
