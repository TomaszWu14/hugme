FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    DATABASE=/data/hugme.db COOKIE_SECURE=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 1000 hugme && mkdir -p /data && chown hugme /data

COPY --chown=hugme . .
USER hugme

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/zdrowie')"
# ponytail: 1 worker + wątki – SQLite w prototypie; przy PostgreSQL zwiększ --workers
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "8", "--access-logfile", "-", "app:create_app()"]
