#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ "$#" -ne 1 ]; then echo 'Uso: bash esegui_nuove_note.command /percorso/NUOVO_DATASET.json'; exit 2; fi
python3 prova_x0_x1.py --dataset "$1"
