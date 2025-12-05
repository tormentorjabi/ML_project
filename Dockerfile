FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv pip install --system --no-cache .

COPY configs ./configs

CMD ["python", "-m", "src.experiments.run_experiment", "--config", "configs/experiment.yaml"]

