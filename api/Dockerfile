FROM python:3.12-slim

WORKDIR /api

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /api

RUN pip install --no-cache-dir -r requirements.txt

COPY . /api

ENV PORT 8000

CMD uvicorn --app-dir src main:app --host 0.0.0.0 --port $PORT