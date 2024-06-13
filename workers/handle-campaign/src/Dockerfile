# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.6-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["app.py"]
