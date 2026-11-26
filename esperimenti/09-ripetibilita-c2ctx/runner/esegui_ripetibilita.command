#!/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
python3 test_ripetibilita.py
python3 prova_ripetibilita.py --repeats 3 --scope focus
