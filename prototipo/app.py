"""Interfaccia locale dimostrativa UC-01: nessuna scrittura delle note."""
from __future__ import annotations

import json
import queue
import threading
import tkinter as tk
from tkinter import ttk

from pipeline.demo_core import analyze_note, DemoInputError

DEFAULT_URL = 'http://127.0.0.1:8091/v1'


class NoteDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Assistente AI locale — UC-01')
        self.geometry('920x740')
        self.minsize(720, 600)
        self.pending = queue.Queue()
        self._busy = False
        self._build()
        self.after(120, self._poll)

    def _build(self):
        page = ttk.Frame(self, padding=18)
        page.pack(fill='both', expand=True)
        ttk.Label(page, text='Analisi locale delle note', font=('Arial', 19, 'bold')).pack(anchor='w')
        ttk.Label(page, text='Prototipo sperimentale · X0 + C2 + Z + S2-V · nessuna azione viene salvata').pack(anchor='w', pady=(3,14))
        ttk.Label(page, text='Nota (massimo 600 caratteri)').pack(anchor='w')
        self.input = tk.Text(page, height=6, wrap='word')
        self.input.pack(fill='x', pady=(5,8))
        self.input.insert('1.0', 'Domani devo prenotare il furgone.')
        line = ttk.Frame(page)
        line.pack(fill='x', pady=(0,12))
        ttk.Label(line, text='Server locale').pack(side='left')
        self.url = tk.StringVar(value=DEFAULT_URL)
        ttk.Entry(line, textvariable=self.url, width=35).pack(side='left', padx=8)
        self.run_button = ttk.Button(line, text='Analizza nota', command=self._run)
        self.run_button.pack(side='left')
        self.status = tk.StringVar(value='Pronto. Avvia il server del modello prima di analizzare.')
        ttk.Label(page, textvariable=self.status, wraplength=800).pack(anchor='w', pady=(0,7))
        tabs = ttk.Notebook(page)
        tabs.pack(fill='both', expand=True)
        self.texts = {}
        for name in ('Risultato','Dettagli e limiti','JSON diagnostico'):
            frame = ttk.Frame(tabs, padding=8)
            tabs.add(frame, text=name)
            holder = ttk.Frame(frame)
            holder.pack(fill='both', expand=True)
            box = tk.Text(holder, wrap='word', state='disabled', font=('Arial',11))
            bar = ttk.Scrollbar(holder, command=box.yview)
            box.configure(yscrollcommand=bar.set)
            box.pack(side='left', fill='both', expand=True)
            bar.pack(side='right', fill='y')
            self.texts[name] = box
        self._set_text('Risultato', 'Inserisci una nota e premi «Analizza nota».\n\nIl prototipo propone al massimo una attività o un evento; non modifica file, calendari o promemoria.')

    def _set_text(self, tab, text):
        box = self.texts[tab]
        box.config(state='normal')
        box.delete('1.0','end')
        box.insert('1.0', text)
        box.config(state='disabled')

    def _run(self):
        if self._busy:
            return
        note = self.input.get('1.0','end').strip()
        if not note or len(note)>600:
            self.status.set('Inserisci una nota fra 1 e 600 caratteri.')
            return
        url = self.url.get().strip()
        if not url.startswith('http://127.0.0.1:') and not url.startswith('http://localhost:'):
            self.status.set('Per questa demo sono consentiti solo server in locale (127.0.0.1 o localhost).')
            return
        self._busy = True
        self.run_button.config(state='disabled')
        self.status.set('Analisi in corso sul modello locale…')
        threading.Thread(target=self._worker, args=(note,url), daemon=True).start()

    def _worker(self, note, url):
        try:
            result = analyze_note(note, url=url, timeout=180)
            self.pending.put(('result',result))
        except Exception as exc:
            self.pending.put(('error',f'{type(exc).__name__}: {exc}'))

    def _poll(self):
        try:
            while True:
                kind, payload = self.pending.get_nowait()
                self._busy = False
                self.run_button.config(state='normal')
                if kind == 'error':
                    self.status.set('Analisi non riuscita. Controlla che il server locale sia attivo.')
                    self._set_text('Risultato','Errore: '+payload)
                else:
                    self._show(payload)
        except queue.Empty:
            pass
        self.after(120, self._poll)

    def _show(self, r):
        option = r['selected']
        if option:
            headline = 'PROPOSTA (non eseguita)\n\n' + option['evidence']
            headline += '\n\nTipo: '+ option['kind'] +'\nIntenzione: '+option['intent']
        else:
            headline = 'NESSUNA PROPOSTA\n\nNon è stata individuata una proposta selezionabile secondo le regole del prototipo.'
        self._set_text('Risultato', headline + '\n\nEstratti individuati: '+str(len(r['quotes']))+'\nCandidati: '+str(len(r['candidates'])))
        diagnostics = ['Modello: '+str(r['model']), 'Chiamate al modello: '+str(r['model_calls']),
                       'Scritture eseguite: 0', 'Conferme eseguite: nessuna',
                       'Il risultato è una simulazione. Non sostituisce la verifica manuale.',
                       '', 'Errori:']
        diagnostics += ['- '+str(e) for e in r['errors']] or ['- nessuno segnalato']
        diagnostics += ['', 'Avvertenze:']
        diagnostics += ['- '+str(n) for n in r['notices']] or ['- nessuna']
        diagnostics += ['', 'Candidati:']
        for c in r['candidates']:
            diagnostics += ['- '+c['evidence']+' | '+c['kind']+' / '+c['intent'] +
                            ' | eleggibile='+str(c['eligible']) + ' | motivi='+str(c['selector_reasons'])]
        self._set_text('Dettagli e limiti','\n'.join(diagnostics))
        self._set_text('JSON diagnostico',json.dumps(r, ensure_ascii=False, indent=2, default=str))
        self.status.set('Analisi completata. Nessun dato salvato.')


if __name__ == '__main__':
    NoteDemo().mainloop()
