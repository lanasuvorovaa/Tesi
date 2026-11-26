#!/usr/bin/env python3
"""Verifica la preregistrazione senza leggere il gold (e senza inferenza)."""
import hashlib,json
from pathlib import Path
from datetime import datetime
HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'MANIFEST_PRE_REGISTRAZIONE.json').read_text(encoding='utf-8'))
p=HERE/'note_test40_INPUT.json'
real=hashlib.sha256(p.read_bytes()).hexdigest()
assert real==manifest['files_sha256']['note_test40_INPUT.json'], 'Hash dataset differente: test NON congelato'
cases=json.loads(p.read_text(encoding='utf-8'))['casi']
assert len(cases)==40
assert len({r['id'] for r in cases})==40
for r in cases:
 assert isinstance(r['nota'],str) and r['nota'].strip()
 assert r['id'].startswith('UC01-S2TEST-')
 assert datetime.fromisoformat(r['reference_datetime'])
print('OK — 40 note, ID univoci, JSON valido, SHA-256 del dataset verificato')
print('Dataset SHA-256:',real)
