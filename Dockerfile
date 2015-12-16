FROM python:3.4
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
ENV APP_SETTINGS=rebase.common.config.DevelopmentConfig
ENTRYPOINT ["python", "./manage"]
CMD ["runserver", "-h", "0.0.0.0", "-p", "5000"]
