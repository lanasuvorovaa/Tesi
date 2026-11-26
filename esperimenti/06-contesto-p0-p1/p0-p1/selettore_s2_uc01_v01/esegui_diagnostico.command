#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest -v test_s2.py
python3 replay_diagnostico.py
