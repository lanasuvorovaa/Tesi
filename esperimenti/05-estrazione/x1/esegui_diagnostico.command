#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 prova_x0_x1.py --dataset note_test40_DIAGNOSTICO.json
