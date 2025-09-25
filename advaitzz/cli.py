#!/usr/bin/env python3
"""
ADVAITZZ CLI - Dork generator and recon helper
"""
import sys
from advaitzz.banner_anim import print_banner, spinner
from advaitzz.template_manager import TemplateManager
from advaitzz.history import HistoryDB

print_banner()

tm = TemplateManager()
history_db = HistoryDB()

def main():
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

if __name__ == "__main__":
    main()
