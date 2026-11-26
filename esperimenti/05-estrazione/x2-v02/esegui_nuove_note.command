#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ "$#" -ne 1 ]; then echo "Uso: bash esegui_nuove_note.command /percorso/nuove_note.json"; exit 2; fi
python3 prova_x0_x1_x2.py --dataset "$1"
