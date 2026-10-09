FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# deps nativas para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn
COPY . .

# EXPONE tu puerto “interno” (no obliga a EB, pero documenta)
EXPOSE 8000

# 📌 Usar $PORT si existe (EB), si no 8000
CMD ["bash", "-lc", "gunicorn -b 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 wsgi:application"]

