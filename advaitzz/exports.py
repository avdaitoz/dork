import csv
import json
import pandas as pd

def export_results(results, filename, fmt):
    fmt = fmt.lower()
    if fmt == 'txt':
        with open(filename, 'w') as f:
            for r in results:
                f.write(r['dork'] + "\n")
    elif fmt == 'csv':
        keys = results[0].keys() if results else []
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
    elif fmt == 'json':
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    elif fmt == 'xlsx':
        df = pd.DataFrame(results)
        df.to_excel(filename, index=False)
