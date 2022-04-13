FROM python:3.9

RUN pip install requests pandas && mkdir /data

COPY extract.py ./extract.py

ENTRYPOINT [ "python", "extract.py" ]