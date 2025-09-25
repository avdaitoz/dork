#!/usr/bin/env python3
"""
ADVAITZZ GUI - PySimpleGUI front-end for dork generation and passive recon
Portable & standalone (no venv required)
"""
import os
import sys
import threading
from pathlib import Path
import time

# Attempt to import PySimpleGUI
try:
    import PySimpleGUI as sg
except ImportError:
    print("Missing dependency: PySimpleGUI. Install with: pip install PySimpleGUI")
    sys.exit(1)

# Import local modules
try:
    from advaitzz.template_manager import TemplateManager
    from advaitzz.history import HistoryDB
    from advaitzz.api_keys import APIKeyStore
    from advaitzz.exports import export_results
except ModuleNotFoundError:
    # Try to add current dir to sys.path if running as standalone
    sys.path.insert(0, str(Path(__file__).parent))
    from template_manager import TemplateManager
    from history import HistoryDB
    from api_keys import APIKeyStore
    from exports import export_results

# Paths
BASE = Path(__file__).resolve().parent
STATIC_DIR = BASE / "static"
BANNER_FILE = STATIC_DIR / "banner.png"

# Basic UI theme
sg.theme('DarkBlue14')

# ASCII banner fallback
ASCII_BANNER = r"""
    ___  ____  __      __    _ _______ ___ _______ 
   / _ \/ __ \/ /     / /   (_) ___/ // / ___/ / 
  / , _/ /_/ / /__   / /__ / / /__/ _  / /__/ /  
 /_/|_|\____/____/  /____//_/\___/_//_/\___/_/   
                                                  
               ADVAITZZ - Dork & Recon Tool
"""

# Initialize managers
tm = TemplateManager()
history_db = HistoryDB()
apikey_store = APIKeyStore()

# Left column: controls
layout_left = [
    [sg.Text('Target Domain')],
    [sg.Input(key='-DOMAIN-', size=(30,1))],
    [sg.Text('Categories')],
]

for cat in tm.list_categories():
    key = f"-CAT-{cat.replace(' ','_')}-"
    layout_left.append([sg.Checkbox(cat, key=key, default=True)])

layout_left += [[sg.Button('Generate', key='-GEN-'), sg.Button('Export', key='-EXPORT-')]]

# Right column: results
layout_right = [
    [sg.Text('Results')],
    [sg.Multiline(key='-OUT-', size=(80,20))]
]

# Tab layout
tabs = [
    sg.Tab('Dork Generator', [[sg.Column(layout_left), sg.VerticalSeparator(), sg.Column(layout_right)]])
]

layout = [
    [sg.Image(str(BANNER_FILE)) if BANNER_FILE.exists() else sg.Text(ASCII_BANNER, font=('Courier', 14))],
    [sg.TabGroup([tabs], key='-TABGROUP-', expand_x=True, expand_y=True)],
    [sg.StatusBar('', key='-STATUS-', size=(100,1))]
]

window = sg.Window('ADVAITZZ', layout, resizable=True, finalize=True)

# Spinner animation helper
def spinner(duration=1.5):
    for _ in range(int(duration/0.1)):
        for sym in "|/-\\":
            window['-STATUS-'].update(f'Generating... {sym}')
            time.sleep(0.1)

# Event loop
while True:
    event, values = window.read(timeout=100)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    if event == '-GEN-':
        domain = values['-DOMAIN-'].strip()
        if not domain:
            window['-STATUS-'].update('Enter a domain first')
            continue

        # run spinner animation in separate thread
        t = threading.Thread(target=spinner)
        t.start()

        # collect checked categories
        cats = [cat for cat in tm.list_categories() if values.get(f"-CAT-{cat.replace(' ','_')}-")]
        results = []
        for c in cats:
            for tpl in tm.get_templates(c):
                results.append({'domain': domain, 'category': c, 'dork': tpl.format(d=domain)})

        t.join()  # ensure spinner finishes

        window['-OUT-'].update('\n'.join(r['dork'] for r in results))
        window['-STATUS-'].update(f'Generated {len(results)} dorks')
        history_db.record_run([domain], cats, '', len(results))

    if event == '-EXPORT-':
        text = values['-OUT-'].strip()
        if not text:
            window['-STATUS-'].update('Nothing to export')
            continue
        fn = sg.popup_get_file('Save dorks as', save_as=True, no_window=True,
                               default_extension='txt', file_types=(('Text','*.txt'),
                                                                    ('CSV','*.csv'),
                                                                    ('JSON','*.json'),
                                                                    ('Excel','*.xlsx')))
        if fn:
            results = [{'domain':'','category':'','dork':l} for l in text.splitlines() if l.strip()]
            fmt = fn.split('.')[-1]
            try:
                export_results(results, fn, fmt)
                window['-STATUS-'].update(f'Saved {len(results)} dorks to {fn}')
            except Exception as e:
                window['-STATUS-'].update(f'Error saving: {e}')

window.close()
