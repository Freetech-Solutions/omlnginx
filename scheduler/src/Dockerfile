# syntax=docker/dockerfile:1.4
FROM python:3.8-alpine

RUN apk add gcc musl-dev

WORKDIR /app

COPY requirements.txt /app
RUN  pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]
