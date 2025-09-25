#!/usr/bin/env python3
"""
ADVAITZZ - All-in-one CLI + GUI Google Dork & Recon Tool
"""

import sys, os, time, json, csv
from pathlib import Path

# External dependencies
try:
    import PySimpleGUI as sg
except ImportError:
    print("Install PySimpleGUI: pip install PySimpleGUI")
    raise

try:
    import pyfiglet
except ImportError:
    print("Install pyfiglet: pip install pyfiglet")
    raise

try:
    import pandas as pd
except ImportError:
    print("Install pandas: pip install pandas (optional if XLSX export is needed)")

# -----------------------------
# Banner & Animation Functions
# -----------------------------
def show_banner(animated=True, text="ADVAITZZ"):
    try:
        f = pyfiglet.Figlet(font="slant")
        banner_text = f.renderText(text)
    except Exception:
        banner_text = text
    if animated:
        for ch in banner_text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(0.002)
    else:
        sys.stdout.write(banner_text)
    sys.stdout.write("\n>>> Google Dork & Recon Tool <<<\n\n")

def spinner(duration=1.5, message="Processing"):
    frames = ["|", "/", "-", "\\"]
    end = time.time() + duration
    while time.time() < end:
        for f in frames:
            sys.stdout.write(f"\r{message}... {f}")
            sys.stdout.flush()
            time.sleep(0.08)
    sys.stdout.write("\r")

# -----------------------------
# Template Manager
# -----------------------------
class TemplateManager:
    def __init__(self):
        self.templates = {
            "Login Pages": [
                "site:{d} inurl:login",
                "site:{d} intitle:login",
                "site:{d} inurl:signin"
            ],
            "Documents": [
                "site:{d} ext:pdf",
                "site:{d} ext:docx",
                "site:{d} ext:xlsx"
            ],
            "Index Of": [
                "site:{d} intitle:index.of"
            ]
        }

    def list_categories(self):
        return list(self.templates.keys())

    def get_templates(self, cat):
        return self.templates.get(cat, [])

# -----------------------------
# History & API Storage
# -----------------------------
HISTORY_FILE = Path("advaitzz_history.json")
API_FILE = Path("advaitzz_apikeys.json")

def load_history():
    if HISTORY_FILE.exists(): 
        return json.loads(HISTORY_FILE.read_text())
    return []

def save_history(data):
    HISTORY_FILE.write_text(json.dumps(data, indent=2))

def record_run(domains, categories, count):
    data = load_history()
    data.append({"domains": domains, "categories": categories, "count": count})
    save_history(data)

# -----------------------------
# Export Function
# -----------------------------
def export_results(results, filename):
    fmt = filename.split(".")[-1].lower()
    if fmt=="txt":
        Path(filename).write_text("\n".join(r["dork"] for r in results))
    elif fmt=="csv":
        keys = results[0].keys() if results else ["dork"]
        with open(filename,"w",newline="",encoding="utf-8") as fh:
            writer = csv.DictWriter(fh,fieldnames=keys)
            writer.writeheader()
            for r in results: writer.writerow(r)
    elif fmt=="json":
        Path(filename).write_text(json.dumps(results, indent=2))
    elif fmt in ["xlsx","xls"]:
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)
    else:
        raise ValueError("Unsupported format: "+fmt)

# -----------------------------
# CLI Mode
# -----------------------------
def run_cli():
    show_banner(animated=True)
    domain = input("Enter target domain: ").strip()
    if not domain:
        print("No domain entered. Exiting...")
        return
    tm = TemplateManager()
    categories = tm.list_categories()
    results = []
    for c in categories:
        for tpl in tm.get_templates(c):
            results.append({"domain": domain, "category": c, "dork": tpl.format(d=domain)})
    print("\nGenerated Dorks:\n")
    for r in results:
        print(r["dork"])
    record_run([domain], categories, len(results))
    save = input("\nSave results? (filename.txt/csv/json/xlsx or ENTER skip): ").strip()
    if save:
        export_results(results, save)
        print(f"Saved {len(results)} dorks to {save}")

# -----------------------------
# GUI Mode
# -----------------------------
def run_gui():
    tm = TemplateManager()
    # Left Column
    layout_left = [
        [sg.Text("Domain")],
        [sg.Input(key="-DOMAIN-")],
        [sg.Text("Categories")]
    ]
    for c in tm.list_categories():
        layout_left.append([sg.Checkbox(c, key=f"-CAT-{c}-", default=True)])
    layout_left.append([sg.Button("Generate", key="-GEN-"), sg.Button("Export", key="-EXPORT-")])

    # Right Column
    layout_right = [
        [sg.Text("Results")],
        [sg.Multiline(key="-OUT-", size=(80,20))]
    ]

    # Full Layout
    layout = [
        [sg.Text("ADVAITZZ", font=("Any", 20))],
        [sg.Column(layout_left), sg.VerticalSeparator(), sg.Column(layout_right)],
        [sg.StatusBar("", size=(100,1), key="-STATUS-")]
    ]

    window = sg.Window("ADVAITZZ", layout, resizable=True, finalize=True)

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        if event == "-GEN-":
            domain = (values.get("-DOMAIN-") or "").strip()
            if not domain:
                window["-STATUS-"].update("Enter domain")
                continue
            cats = [c for c in tm.list_categories() if values.get(f"-CAT-{c}-")]
            results = []
            for c in cats:
                for tpl in tm.get_templates(c):
                    results.append({"domain": domain, "category": c, "dork": tpl.format(d=domain)})
            window["-OUT-"].update("\n".join(r["dork"] for r in results))
            window["-STATUS-"].update(f"Generated {len(results)} dorks")
            record_run([domain], cats, len(results))
        if event == "-EXPORT-":
            txt = (values.get("-OUT-") or "").strip()
            if not txt:
                continue
            fn = sg.popup_get_file("Save as", save_as=True, no_window=True, default_extension="txt",
                                   file_types=(("Text","*.txt"),("CSV","*.csv"),("JSON","*.json"),("Excel","*.xlsx")))
            if fn:
                export_results([{"dork": l} for l in txt.splitlines() if l.strip()], fn)
                window["-STATUS-"].update(f"Saved {len(txt.splitlines())} dorks to {fn}")

    window.close()

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    show_banner(animated=True)
    mode = input("Run in CLI or GUI? [cli/gui]: ").strip().lower()
    if mode == "gui":
        run_gui()
    else:
        run_cli()
