#!/bin/bash
set -euo pipefail
mkdir -p "$HOME/models"
QWEN="$HOME/models/qwen3.5-2b-q4_k_m.gguf"
LFM="$HOME/models/lfm2.5-1.2b-instruct-q4_k_m.gguf"
if [ ! -f "$HOME/models/qwen3-1.7b-q4.gguf" ]; then
  echo 'Non trovo il modello baseline ~/models/qwen3-1.7b-q4.gguf'; exit 1
fi
if [ ! -f "$QWEN" ] && [ ! -f "$HOME/models/Qwen_Qwen3.5-2B-Q4_K_M.gguf" ]; then
  echo 'Scarico Qwen3.5-2B Q4_K_M (circa 1,4 GB)'
  curl --fail --location --retry 3 --continue-at - --output "$QWEN" \
    'https://huggingface.co/bartowski/Qwen_Qwen3.5-2B-GGUF/resolve/main/Qwen_Qwen3.5-2B-Q4_K_M.gguf'
fi
if [ ! -f "$LFM" ] && [ ! -f "$HOME/models/LFM2.5-1.2B-Instruct-Q4_K_M.gguf" ]; then
  echo 'Scarico LFM2.5-1.2B-Instruct Q4_K_M (circa 700 MB)'
  curl --fail --location --retry 3 --continue-at - --output "$LFM" \
    'https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF/resolve/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf'
fi
python3 - "${QWEN}" "${LFM}" <<'PY'
import sys
from pathlib import Path
for p in map(Path,sys.argv[1:]):
 if not p.is_file():
  print('Il modello ha un altro nome oppure manca:',p)
  continue
 print(p.name, ':', round(p.stat().st_size/1e9, 2),'GB')
 with p.open('rb') as f:
  if f.read(4)!=b'GGUF':raise SystemExit('Formato GGUF non valido: '+str(p))
PY
