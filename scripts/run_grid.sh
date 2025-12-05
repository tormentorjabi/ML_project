#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH="${1:-configs/grid.yaml}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

NETWORK_NAME="$(basename "${ROOT_DIR}" | tr '[:upper:]' '[:lower:]')_default"

docker run --rm \
  --network "${NETWORK_NAME}" \
  -e S3_ENDPOINT_URL=http://minio:9000 \
  -e S3_ACCESS_KEY=admin \
  -e S3_SECRET_KEY=admin123 \
  -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 \
  -v "${ROOT_DIR}/models:/app/models" \
  -v "${ROOT_DIR}/${CONFIG_PATH}:/app/configs/grid_active.yaml:ro" \
  taxi-experiments \
  python -m src.experiments.run_grid --config configs/grid_active.yaml

