FROM python:3.13-alpine3.20

LABEL authors="iamlucky1990@gmail.com"

RUN adduser --disabled-password --no-create-home django-user

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN mkdir -p /vol/web/media
RUN chown -R django-user /vol/
RUN chmod -R 755 /vol/web/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER django-user
