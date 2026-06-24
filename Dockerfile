FROM python:3.13-slim AS builder

WORKDIR /build

COPY pyproject.toml ./
COPY app/ ./app/

RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /build/dist/*.whl ./
RUN pip install --no-cache-dir ./*.whl && rm -f ./*.whl

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
