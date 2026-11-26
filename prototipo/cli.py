"""CLI compatta del prototipo UC-01. Non salva dati."""
import argparse
import json
from pipeline.demo_core import analyze_note

def main():
    parser=argparse.ArgumentParser(description='UC-01, analisi di note in locale')
    parser.add_argument('note', help='Testo della nota')
    parser.add_argument('--url',default='http://127.0.0.1:8091/v1',help='Endpoint locale OpenAI-compatible')
    args=parser.parse_args()
    if not (args.url.startswith('http://127.0.0.1:') or args.url.startswith('http://localhost:')):
        parser.error('Sono ammessi solo endpoint locali.')
    outcome=analyze_note(args.note,url=args.url,timeout=180)
    print(json.dumps({k:outcome[k] for k in ('decision','selected','quotes','candidates','errors','notices','writes_performed')},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
