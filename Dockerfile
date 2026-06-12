FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG MT_MODEL
ARG MODEL_CACHE_DIR

WORKDIR /app

COPY core/requirements-torch.txt /app/core/requirements-torch.txt
RUN pip install --no-cache-dir -r /app/core/requirements-torch.txt

COPY core/requirements.txt /app/core/requirements.txt
RUN pip install --no-cache-dir -r /app/core/requirements.txt

COPY core/src /app/src
COPY scripts /app/scripts

RUN MT_MODEL="${MT_MODEL}" MODEL_CACHE_DIR="${MODEL_CACHE_DIR}" python /app/scripts/prefetch_model.py

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.main:app --host \"$HOST\" --port \"$PORT\""]
