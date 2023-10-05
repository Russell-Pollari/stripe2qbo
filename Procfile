web: alembic upgrade head && python -m uvicorn stripe2qbo.api.app:app --port $PORT --host 0.0.0.0
worker: celery -A stripe2qbo.workers.sync_worker worker
