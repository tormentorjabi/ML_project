#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "Building training image..."
docker build -t taxi-experiments .

echo "Starting MinIO + MLflow via docker compose..."
docker compose up -d

echo "Bootstrap complete. MinIO console: http://localhost:9001 | MLflow UI: http://localhost:5000"

