#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BASE="$HOME/Desktop/confronto_slm_uc01_v01"
if [ ! -f "$BASE/runtime/llama.cpp/build/bin/llama-server" ]; then
  echo "Non trovo il runtime del confronto precedente in: $BASE/runtime/llama.cpp/build/bin/llama-server"
  echo "Mantieni sul Desktop la cartella confronto_slm_uc01_v01 utilizzata nei test precedenti."
  exit 1
fi
if [ ! -f "$HOME/models/qwen3-1.7b-q4.gguf" ]; then
  echo "Non trovo il modello: $HOME/models/qwen3-1.7b-q4.gguf"
  exit 1
fi
if [ ! -x "$BASE/.venv/bin/python" ]; then
  echo "Non trovo l'ambiente Python del confronto precedente: $BASE/.venv/bin/python"
  echo "Serve l'ambiente già preparato con jsonschema."
  exit 1
fi
PY="$BASE/.venv/bin/python"
cd "$ROOT"
echo "Verifica preliminare del codice:"
"$PY" -m unittest discover -s pipeline_demo -p 'test_demo.py' -q
"$PY" -m unittest discover -s . -p 'test_experiment.py' -q
echo "Avvio confronto C0 vs C1 (24 note development, stesso Qwen3-1.7B):"
"$PY" prova_c1.py --base "$BASE"
