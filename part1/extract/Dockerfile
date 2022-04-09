FROM python:3.9

RUN pip install requests 

COPY extract.py ./extract.py

ENTRYPOINT [ "python", "extract.py" ]