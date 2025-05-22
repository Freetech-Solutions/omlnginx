# syntax=docker/dockerfile:1.4
FROM python:3.12-alpine3.19 as builder

WORKDIR /app

RUN apk add gcc musl-dev python3-dev build-base git

RUN apk update && apk add ca-certificates

RUN pip3 install --upgrade pip

ADD . /app

RUN pip3 install -r requirements.txt

FROM python:3.12-alpine3.19 AS run

RUN apk add tzdata

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . /app

CMD ["python3", "app.py"]
