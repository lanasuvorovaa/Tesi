#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
# L'audit I1 è incluso nella preparazione della prova online.
# Non eseguire --offline-only immediatamente prima: creerebbe
# una cartella di output con lo stesso timestamp al secondo.
python3 prova_c2_ctx.py
