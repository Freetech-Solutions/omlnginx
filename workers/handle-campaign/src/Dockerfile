# syntax=docker/dockerfile:1.4
FROM python:3.6-alpine

WORKDIR /app

RUN apk add gcc musl-dev

RUN pip3 install --upgrade pip

ADD . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["/app/app.py"]
