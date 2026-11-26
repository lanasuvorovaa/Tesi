#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if [ ! -f "$ROOT/.venv/bin/python" ]; then
  echo 'Manca ambiente Python: esegui prima bash 01_prepara_runtime.command'; exit 1
fi
"$ROOT/.venv/bin/python" "$ROOT/confronta.py" --fase 1
