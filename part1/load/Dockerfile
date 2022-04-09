FROM python:3.9

RUN pip install minio

COPY load.py load.py

COPY config.yaml config.yaml

ENTRYPOINT [ "python", "load.py" ]