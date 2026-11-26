#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
python3 -m unittest -q test_confronta.py pipeline_demo/test_demo.py
