#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 prova_c2_ctx.py --offline-only
python3 prova_c2_ctx.py
