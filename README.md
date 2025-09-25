# ADVAITZZ

Stylish Google Dork & Recon Scanner with interactive CLI and GUI.  
Runs on all platforms, legal recon only.

## Features

- Interactive CLI & GUI
- Multiple categories: login pages, documents, index-of, secrets, cloud, subdomains
- Batch mode (multi-domain)
- Export results: TXT, CSV, JSON, Excel
- Animated ASCII banner & stylish GUI
- History tracking & template manager
- API key management
- Legal disclaimer: Only test targets you are authorized to

## Installation

Clone the repo:

```bash
git clone https://github.com/shantnoothakur/dorkk.git
cd dorkk
Optional: create virtual environment (recommended):

bash
Copy code
python3 -m venv venv
. venv/bin/activate   # Linux/macOS
.\venv\Scripts\activate  # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt       # CLI only
pip install -r requirements_gui.txt   # GUI
Install editable module:

bash
Copy code
pip install -e .
Run CLI:

bash
Copy code
advaitzz
# or
python -m advaitzz.cli
Run GUI:

bash
Copy code
python -m advaitzz.gui
Usage Examples
Interactive CLI:

bash
Copy code
advaitzz
Non-interactive:

bash
Copy code
advaitzz example.com --categories login,docs --output results.txt --format txt
Batch mode:

bash
Copy code
advaitzz --input domains.txt --categories login,docs --output batch_results.txt
