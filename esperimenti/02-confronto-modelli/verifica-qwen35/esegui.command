#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/Desktop/confronto_slm_uc01_v01"
if [ ! -f "$BASE/.venv/bin/python" ]; then
  echo "Non trovo l'ambiente Python del confronto precedente in: $BASE"
  echo 'Assicurati che la cartella confronto_slm_uc01_v01 sia ancora sul Desktop.'
  exit 1
fi
if [ ! -f "$BASE/runtime/llama.cpp/build/bin/llama-server" ]; then
  echo 'Non trovo llama-server aggiornato: serve il runtime del confronto precedente.'
  exit 1
fi
"$BASE/.venv/bin/python" "$ROOT/verifica.py" --base "$BASE"
