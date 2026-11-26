#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/Desktop/confronto_slm_uc01_v01"
PY="$BASE/.venv/bin/python"
if [ ! -x "$PY" ]; then echo "Ambiente Python non trovato: $PY"; exit 1; fi
if [ ! -x "$BASE/runtime/llama.cpp/build/bin/llama-server" ]; then echo "Runtime llama-server non trovato"; exit 1; fi
if [ ! -f "$HOME/models/qwen3-1.7b-q4.gguf" ]; then echo "Modello Qwen3 non trovato"; exit 1; fi
cd "$ROOT"
"$PY" -m unittest discover -s . -p 'test_s1.py' -q
"$PY" prova_s1.py --base "$BASE"
