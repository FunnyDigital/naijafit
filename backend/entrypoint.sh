#!/bin/sh
set -e

echo "[entrypoint] Starting NaijaFit on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
