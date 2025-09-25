import json
from pathlib import Path

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
