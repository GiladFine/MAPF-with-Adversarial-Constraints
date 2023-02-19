FROM python:3.9-buster
WORKDIR /gilad

ENV PYTHONPATH ./:

RUN pip install -r requirements.txt
