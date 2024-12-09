# syntax=docker/dockerfile:1.4
FROM python:3.8-alpine as builder

WORKDIR /app

COPY requirements.txt /app
RUN  pip3 install -r requirements.txt

FROM python:3.8-alpine AS run

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . /app

CMD ["python3", "app.py"]
