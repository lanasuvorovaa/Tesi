#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ $# -lt 1 ]]; then echo 'Uso: bash esegui_nuove_note.command /percorso/nuove_note.json'; exit 2; fi
python3 prova_s2_nuove_note.py --dataset "$1"
