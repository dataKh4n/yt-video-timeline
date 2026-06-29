FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# YOUTUBE_API_KEY must be provided at runtime via env var
CMD ["sh", "-c", "gunicorn web_app:app --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120"]
