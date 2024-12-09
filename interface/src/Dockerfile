# syntax=docker/dockerfile:1.4
FROM python:3.8-alpine AS builder

WORKDIR /app

COPY ./requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

FROM python:3.8-alpine AS run

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . /app

#ENTRYPOINT ["python3"]
CMD ["python3", "app.py"]
