#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
S2="$HOME/Desktop/selettore_s2_uc01_v01"
if [ ! -f "$S2/esegui_nuove_note.command" ]; then
 echo "ERRORE: estrai selettore_s2_uc01_v01 sul Desktop, accanto al test set."
 exit 1
fi
python3 "$HERE/verifica_dataset.py"
cd "$S2"
bash esegui_nuove_note.command "$HERE/note_test40_INPUT.json"
