FROM python:3.8

RUN pip install minio

COPY load.py load.py

ENTRYPOINT [ "python", "load.py" ]