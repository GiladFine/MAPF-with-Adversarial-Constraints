FROM python:3.9-buster

ENV PYTHONPATH ./:

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt
