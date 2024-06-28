# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.6-alpine AS builder

WORKDIR /app

RUN apk add gcc musl-dev

RUN pip3 install --upgrade pip

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]
