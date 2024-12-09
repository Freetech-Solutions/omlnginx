# syntax=docker/dockerfile:1.4
FROM python:3.6-alpine as builder

WORKDIR /app

RUN apk add gcc musl-dev

RUN pip3 install --upgrade pip

ADD . /app

RUN pip3 install -r requirements.txt

FROM python:3.6-alpine AS run

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . /app

CMD ["python3", "app.py"]
