#!/usr/bin/env python3
"""
advaitzz - single-file CLI + GUI tool with animated ASCII banner
"""

from pathlib import Path
import sys, time, json, csv, threading

# Optional dependencies will be imported where needed (GUI / xlsx / figlet)
# so the package can be installed and still run CLI without GUI deps.

# -------------------------
# Banner & spinner
# -------------------------
def _render_banner_text(text="ADVAITZZ", font="slant"):
    try:
        import pyfiglet
        f = pyfiglet.Figlet(font=font)
        return f.renderText(text)
    except Exception:
        # fallback plain
        return text + "\n"

def show_banner(animated=True, text="ADVAITZZ", font="slant", char_delay=0.002):
    banner = _render_banner_text(text=text, font=font)
    if animated:
        for ch in banner:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(char_delay)
    else:
        sys.stdout.write(banner)
    sys.stdout.write("\n>>> ADVAITZZ — Google Dork & Recon Tool <<<\n\n")
    sys.stdout.flush()

def spinner(duration=1.5, message="Processing"):
    frames = ["|", "/", "-", "\\"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r{message}... {frames[i % 4]}")
        sys.stdout.flush()
        time.sleep(0.12)
        i += 1
    sys.stdout.write("\r")
    sys.stdout.flush()

# -------------------------
# Template manager
# -------------------------
class TemplateManager:
    def __init__(self):
        self.templates = {
            "Login Pages": [
                "site:{d} inurl:login",
                "site:{d} intitle:login",
                "site:{d} inurl:signin",
            ],
            "Documents": [
                "site:{d} ext:pdf",
                "site:{d} ext:docx",
                "site:{d} ext:xlsx",
            ],
            "Index Of": [
                "site:{d} intitle:index.of",
            ],
            "Subdomains": [
                "site:*.{d} -www.{d}"
            ]
        }

    def list_categories(self):
        return list(self.templates.keys())

    def get_templates(self, cat):
        return self.templates.get(cat, [])

# -------------------------
# History (file-based)
# -------------------------
HISTORY_PATH = Path("advaitzz_history.json")

class HistoryDB:
    def __init__(self, path=None):
        self.path = HISTORY_PATH if path is None else Path(path)
        if not self.path.exists():
            self._write([])

    def _read(self):
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return []

    def _write(self, data):
        try:
            self.path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def record_run(self, domains, categories, note, count):
        data = self._read()
        data.append({
            "timestamp": time.time(),
            "domains": domains,
            "categories": categories,
            "note": note,
            "count": count
        })
        self._write(data)

    def list_runs(self):
        return self._read()

# -------------------------
# Exports
# -------------------------
def export_results(results, filename):
    fmt = filename.split(".")[-1].lower()
    path = Path(filename)
    if fmt == "txt":
        path.write_text("\n".join(r.get("dork", "") for r in results))
        return
    if fmt == "csv":
        keys = list(results[0].keys()) if results else ["dork"]
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        return
    if fmt == "json":
        path.write_text(json.dumps(results, indent=2))
        return
    if fmt in ("xlsx", "xls"):
        try:
            import pandas as pd
        except Exception as e:
            raise RuntimeError("pandas required to export Excel files: pip install pandas") from e
        df = pd.DataFrame(results)
        df.to_excel(str(path), index=False)
        return
    raise ValueError("Unsupported export format: " + fmt)

# -------------------------
# CLI
# -------------------------
def run_cli_interactive():
    show_banner(animated=True)
    spinner(0.8, message="Starting")

    tm = TemplateManager()
    history = HistoryDB()

    print("Available categories:")
    cats = tm.list_categories()
    for i, c in enumerate(cats, 1):
        print(f" {i}) {c}")
    print("")

    domain = input("Enter target domain (example.com): ").strip()
    if not domain:
        print("No domain provided. Exiting.")
        return

    selection = input("Choose categories (comma-separated numbers or 'all') [all]: ").strip()
    if not selection or selection.lower() == "all":
        selected_categories = cats
    else:
        try:
            indexes = [int(x.strip()) for x in selection.split(",") if x.strip()]
            selected_categories = [cats[i - 1] for i in indexes if 1 <= i <= len(cats)]
        except Exception:
            print("Invalid selection. Exiting.")
            return

    print("\nGenerating dorks...")
    spinner(1.2, message="Generating")
    results = []
    for c in selected_categories:
        for tpl in tm.get_templates(c):
            results.append({"domain": domain, "category": c, "dork": tpl.format(d=domain)})

    print(f"\nGenerated {len(results)} dorks:\n")
    for r in results:
        print(r["dork"])

    history.record_run([domain], selected_categories, "", len(results))

    save = input("\nSave results? (filename.txt/csv/json/xlsx or ENTER to skip): ").strip()
    if save:
        try:
            export_results(results, save)
            print(f"Saved {len(results)} dorks to {save}")
        except Exception as e:
            print("Failed to save file:", e)

# -------------------------
# GUI
# -------------------------
def run_gui():
    # lazy import
    try:
        import PySimpleGUI as sg
    except Exception:
        print("PySimpleGUI not installed. Install with: pip install PySimpleGUI")
        return

    tm = TemplateManager()
    history = HistoryDB()

    # Header: try figlet (console) fallback into multiline
    header_text = _render_banner_text(text="ADVAITZZ", font="slant")
    header_element = None
    try:
        # Use an image banner if exists in current dir advaitzz/static/banner.png
        banner_png = Path(__file__).resolve().parent / "static" / "banner.png"
        if banner_png.exists():
            header_element = sg.Image(str(banner_png))
        else:
            header_element = sg.Multiline(header_text, size=(80,10), font=("Courier", 12),
                                          disabled=True, no_scrollbar=True, background_color=sg.theme_background_color())
    except Exception:
        header_element = sg.Text("ADVAITZZ", font=("Any", 20))

    sg.theme("DarkBlue14")

    layout_left = [
        [sg.Text("Target Domain")],
        [sg.Input(key="-DOMAIN-", size=(30,1))],
        [sg.Text("Categories")]
    ]
    for c in tm.list_categories():
        layout_left.append([sg.Checkbox(c, key=f"-CAT-{c.replace(' ','_')}-", default=True)])
    layout_left.append([sg.Button("Generate", key="-GEN-"), sg.Button("Export", key="-EXPORT-")])

    layout_right = [
        [sg.Text("Results")],
        [sg.Multiline(key="-OUT-", size=(80,20))]
    ]

    layout = [
        [header_element],
        [sg.Column(layout_left), sg.VerticalSeparator(), sg.Column(layout_right)],
        [sg.StatusBar("", key="-STATUS-", size=(100,1))]
    ]

    window = sg.Window("ADVAITZZ", layout, resizable=True, finalize=True)

    def spinner_thread(sec, key="-STATUS-"):
        frames = ["|","/","-","\\"]
        end = time.time() + sec
        i = 0
        while time.time() < end:
            window[key].update(f"Working... {frames[i%4]}")
            time.sleep(0.12)
            i += 1
        window[key].update("")

    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "-GEN-":
            domain = (values.get("-DOMAIN-") or "").strip()
            if not domain:
                window["-STATUS-"].update("Enter a domain first")
                continue

            cats = []
            for c in tm.list_categories():
                key = f"-CAT-{c.replace(' ','_')}-"
                if values.get(key):
                    cats.append(c)

            t = threading.Thread(target=spinner_thread, args=(1.4,), daemon=True)
            t.start()

            results = []
            for c in cats:
                for tpl in tm.get_templates(c):
                    results.append({"domain": domain, "category": c, "dork": tpl.format(d=domain)})

            t.join()
            window["-OUT-"].update("\n".join(r["dork"] for r in results))
            window["-STATUS-"].update(f"Generated {len(results)} dorks")
            try:
                history.record_run([domain], cats, "", len(results))
            except Exception:
                pass

        if event == "-EXPORT-":
            text = (values.get("-OUT-") or "").strip()
            if not text:
                window["-STATUS-"].update("Nothing to export")
                continue
            fn = sg.popup_get_file("Save as", save_as=True, no_window=True, default_extension="txt",
                                   file_types=(("Text","*.txt"),("CSV","*.csv"),("JSON","*.json"),("Excel","*.xlsx")))
            if fn:
                try:
                    export_results([{"dork": l} for l in text.splitlines() if l.strip()], fn)
                    window["-STATUS-"].update(f"Saved {len(text.splitlines())} dorks to {fn}")
                except Exception as e:
                    window["-STATUS-"].update(f"Error saving: {e}")

    window.close()

# -------------------------
# Entrypoint expected by setup.py
# -------------------------
def main():
    # show banner first (animated)
    show_banner(animated=True)
    # ask user or accept an environment hint
    if len(sys.argv) > 1:
        # quick mode: if user passes 'gui' use GUI, if domain present run quick CLI generation
        if "gui" in sys.argv[1:]:
            run_gui()
            return
        else:
            # treat argv as domains to generate quickly
            tm = TemplateManager()
            domains = sys.argv[1:]
            results = []
            for domain in domains:
                for c in tm.list_categories():
                    for tpl in tm.get_templates(c):
                        results.append({"domain": domain, "category": c, "dork": tpl.format(d=domain)})
            for r in results:
                print(r["dork"])
            return

    # otherwise interactive: ask CLI or GUI
    choice = input("Run in CLI or GUI? [cli/gui] (default cli): ").strip().lower()
    if choice == "gui":
        run_gui()
    else:
        run_cli_interactive()

if __name__ == "__main__":
    main()
