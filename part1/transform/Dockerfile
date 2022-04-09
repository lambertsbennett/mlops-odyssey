FROM python:3.8

RUN pip install pandas

COPY transform.py transform.py

ENTRYPOINT [ "python", "transform.py" ]