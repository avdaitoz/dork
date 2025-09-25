#!/usr/bin/env python3
"""
ADVAITZZ - Combined Single Script (CLI + GUI + All Modules)
"""
import sys
import os
import json
import threading
import time
from pathlib import Path

# --- Banner Animations ---
ASCII_BANNER = r"""
    ___  ____  __      __    _ _______ ___ _______ 
   / _ \/ __ \/ /     / /   (_) ___/ // / ___/ / 
  / , _/ /_/ / /__   / /__ / / /__/ _  / /__/ /  
 /_/|_|\____/____/  /____//_/\___/_//_/\___/_/   
                                                  
               ADVAITZZ - Dork & Recon Tool
"""

def print_banner():
    print(ASCII_BANNER)

def spinner(duration=1.5, message="Loading"):
    for _ in range(int(duration/0.1)):
        for sym in "|/-\\":
            sys.stdout.write(f"\r{message}... {sym}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r")

# --- History Module ---
class HistoryDB:
    def __init__(self):
        self.file = Path("advaitzz_history.json")
        if not self.file.exists():
            self.file.write_text("[]")

    def record_run(self, domains, categories, extra, count):
        data = json.loads(self.file.read_text())
        data.append({
            'domains': domains,
            'categories': categories,
            'extra': extra,
            'count': count
        })
        self.file.write_text(json.dumps(data, indent=2))

    def list_runs(self):
        return json.loads(self.file.read_text())

# --- Template Manager ---
class TemplateManager:
    def __init__(self):
        self.templates = {
            'Login Pages': [
                'site:{d} inurl:login',
                'site:{d} intitle:login',
                'site:{d} inurl:signin'
            ],
            'Documents': [
                'site:{d} ext:pdf',
                'site:{d} ext:docx',
                'site:{d} ext:xlsx'
            ],
            'Index Of': [
                'site:{d} intitle:"index of"'
            ]
        }

    def list_categories(self):
        return list(self.templates.keys())

    def get_templates(self, category):
        return self.templates.get(category, [])

    def add_category(self, category):
        if category not in self.templates:
            self.templates[category] = []

    def remove_category(self, category):
        if category in self.templates:
            del self.templates[category]

    def add_template(self, category, tpl):
        if category in self.templates:
            self.templates[category].append(tpl)

    def remove_template(self, category, idx):
        if category in self.templates and 0 <= idx < len(self.templates[category]):
            del self.templates[category][idx]

# --- API Key Storage ---
class APIKeyStore:
    def __init__(self):
        self.file = Path("advaitzz_apikeys.json")
        if not self.file.exists():
            self.file.write_text("{}")

    def load(self):
        return json.loads(self.file.read_text())

    def save(self, data):
        self.file.write_text(json.dumps(data, indent=2))

# --- Export Module ---
def export_results(results, filename, fmt):
    fmt = fmt.lower()
    if fmt == 'txt':
        with open(filename, 'w') as f:
            for r in results:
                f.write(r['dork'] + "\n")
    elif fmt == 'csv':
        import csv
        keys = results[0].keys() if results else []
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
    elif fmt == 'json':
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    elif fmt == 'xlsx':
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)

# --- CLI Dork Generator ---
def run_cli():
    print_banner()
    tm = TemplateManager()
    history_db = HistoryDB()

    print("\nWelcome to ADVAITZZ CLI!\n")
    domain = input("Enter target domain: ").strip()
    if not domain:
        print("Domain is required. Exiting...")
        return

    print("\nAvailable categories:")
    cats = tm.list_categories()
    for idx, cat in enumerate(cats, 1):
        print(f"{idx}. {cat}")

    selected = input("\nSelect categories (comma-separated numbers or 'all'): ").strip()
    if selected.lower() == 'all':
        selected_cats = cats
    else:
        try:
            selected_cats = [cats[int(i)-1] for i in selected.split(',')]
        except Exception:
            print("Invalid selection. Exiting...")
            return

    print("\nGenerating dorks...")
    spinner(1.5)
    results = []
    for c in selected_cats:
        for tpl in tm.get_templates(c):
            results.append(tpl.format(d=domain))

    print(f"\nGenerated {len(results)} dorks:\n")
    for r in results:
        print(r)

    history_db.record_run([domain], selected_cats, '', len(results))

# --- GUI Dork Generator ---
def run_gui():
    try:
        import PySimpleGUI as sg
    except ImportError:
        print("PySimpleGUI not installed. Install with: pip install PySimpleGUI")
        return

    tm = TemplateManager()
    history_db = HistoryDB()
    apikey_store = APIKeyStore()

    sg.theme('DarkBlue14')

    ASCII_BANNER_GUI = r"""
    ___  ____  __      __    _ _______ ___ _______ 
   / _ \/ __ \/ /     / /   (_) ___/ // / ___/ / 
  / , _/ /_/ / /__   / /__ / / /__/ _  / /__/ /  
 /_/|_|\____/____/  /____//_/\___/_//_/\___/_/   
                                                  
               ADVAITZZ - Dork & Recon Tool
"""

    # Left column
    layout_left = [
        [sg.Text('Target Domain')],
        [sg.Input(key='-DOMAIN-', size=(30,1))],
        [sg.Text('Categories')]
    ]
    for cat in tm.list_categories():
        key = f"-CAT-{cat.replace(' ','_')}-"
        layout_left.append([sg.Checkbox(cat, key=key, default=True)])
    layout_left += [[sg.Button('Generate', key='-GEN-'), sg.Button('Export', key='-EXPORT-')]]

    # Right column
    layout_right = [[sg.Text('Results')], [sg.Multiline(key='-OUT-', size=(80,20))]]

    # Tabs
    tabs = [sg.Tab('Dork Generator', [[sg.Column(layout_left), sg.VerticalSeparator(), sg.Column(layout_right)]])]

    layout = [
        [sg.Text(ASCII_BANNER_GUI, font=('Courier',14))],
        [sg.TabGroup([tabs], key='-TABGROUP-', expand_x=True, expand_y=True)],
        [sg.StatusBar('', key='-STATUS-', size=(100,1))]
    ]

    window = sg.Window('ADVAITZZ', layout, resizable=True, finalize=True)

    def spinner_gui(duration=1.5):
        for _ in range(int(duration/0.1)):
            for sym in "|/-\\":
                window['-STATUS-'].update(f'Generating... {sym}')
                time.sleep(0.1)

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == '-GEN-':
            domain = values['-DOMAIN-'].strip()
            if not domain:
                window['-STATUS-'].update('Enter a domain first')
                continue
            t = threading.Thread(target=spinner_gui)
            t.start()
            cats = [cat for cat in tm.list_categories() if values.get(f"-CAT-{cat.replace(' ','_')}-")]
            results = []
            for c in cats:
                for tpl in tm.get_templates(c):
                    results.append({'domain': domain, 'category': c, 'dork': tpl.format(d=domain)})
            t.join()
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

# --- Main Entry ---
def main():
    import argparse
    parser = argparse.ArgumentParser(description="ADVAITZZ - Combined CLI & GUI")
    parser.add_argument("mode", nargs="?", default="cli", choices=["cli","gui"], help="Choose mode: cli or gui")
    args = parser.parse_args()
    if args.mode == "cli":
        run_cli()
    else:
        run_gui()

if __name__ == "__main__":
    main()
