FROM python:3.12-slim

WORKDIR /api

COPY . /api

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "--app-dir", "src", "main:app", "--host", "0.0.0.0", "--port", "8000"]