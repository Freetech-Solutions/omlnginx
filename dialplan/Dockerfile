FROM python:3.12-alpine as build

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r ./requirements.txt

FROM python:3.12-alpine as run

WORKDIR /app
COPY --from=build /usr/local /usr/local
COPY src/* /app/

CMD ["python3",  "app.py" ]