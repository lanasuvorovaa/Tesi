#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/Desktop/confronto_slm_uc01_v01"
PY="$BASE/.venv/bin/python"
if [ ! -x "$PY" ]; then echo "Ambiente Python non trovato: $PY"; exit 1; fi
if [ ! -x "$BASE/runtime/llama.cpp/build/bin/llama-server" ]; then echo "Runtime llama-server non trovato"; exit 1; fi
cd "$ROOT"
"$PY" -m unittest -q test_holdout.py
"$PY" prova_holdout.py --base "$BASE"
