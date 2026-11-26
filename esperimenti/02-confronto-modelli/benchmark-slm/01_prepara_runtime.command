#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/runtime/llama.cpp"
if ! command -v git >/dev/null 2>&1; then
  echo 'Manca git. Installa gli strumenti Xcode Command Line Tools: xcode-select --install'; exit 1
fi
if ! command -v cmake >/dev/null 2>&1; then
  echo 'Manca cmake. Se hai Homebrew: brew install cmake'; exit 1
fi
if ! command -v clang++ >/dev/null 2>&1; then
  echo 'Manca clang++. Installa gli strumenti Xcode Command Line Tools: xcode-select --install'; exit 1
fi
if [ ! -d "$SRC/.git" ]; then
  mkdir -p "$(dirname "$SRC")"
  echo 'Scarico una copia separata di llama.cpp (non tocco la vecchia cartella Tesi - documents).'
  git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$SRC"
fi
echo 'Compilo llama-server per Intel CPU (senza Metal).'
cmake -S "$SRC" -B "$SRC/build" -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_SERVER=ON
cmake --build "$SRC/build" --config Release --target llama-server -j 4
if [ ! -f "$SRC/build/bin/llama-server" ]; then echo 'Compilazione non completa'; exit 1; fi
python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install -r "$ROOT/pipeline_demo/requirements.txt"
echo 'Runtime pronto.'
