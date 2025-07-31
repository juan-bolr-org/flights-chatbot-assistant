FROM python:3.12-slim

WORKDIR /api

COPY . /api

RUN pip install --no-cache-dir -r requirements.txt

ARG PORT

CMD uvicorn --app-dir src main:app --host 0.0.0.0 --port $PORT