FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt server/requirements.txt
RUN pip install -r server/requirements.txt
COPY . server/
RUN useradd --create-home app
USER app
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

FROM base AS development
CMD ["sh", "-c", "alembic -c server/alembic.ini upgrade head && uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM base AS production
CMD ["sh", "-c", "alembic -c server/alembic.ini upgrade head && uvicorn server.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers"]
