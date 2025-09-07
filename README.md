# PathoScope V5

PathoScope V5

PathoScope V5 is an AI-powered disease-mechanism explorer. It ingests gene-expression data, visualizes KEGG pathways, and surfaces potential drug targets with interactive plots (volcano, MA, heatmap) in a modern Flask UI.

Features (at a glance)

Upload & analyze gene expression datasets

Differential expression stats (e.g., via SciPy)

Interactive plots (volcano, MA, heatmap)

KEGG pathway visualization

Drug-target lookups & external resources

Export results (CSV/PDF)

Prerequisites

Python 3.9–3.12 recommended

pip 21+

(Optional) Conda if you prefer managing environments that way

Git (SSH recommended)

Quick Start (Virtualenv)

Text (what you’ll do):
Create a clean virtual environment in the project root, upgrade pip, install compatible deps (with version ranges that avoid NumPy/SciPy conflicts), then run the app.

Code (copy-paste):

# 0) Make sure you're in the project root
cd ~/Desktop/Pathoscope-V5  # adjust path if different

# 1) (Recommended) Start clean by deactivating anything active
conda deactivate 2>/dev/null || true
deactivate 2>/dev/null || true

# 2) Create a fresh venv using system Python
/usr/bin/python3 -m venv venv   # macOS/Linux
# Windows (PowerShell):  py -3 -m venv venv

# 3) Activate it
source venv/bin/activate        # macOS/Linux
# Windows (PowerShell):  venv\Scripts\Activate.ps1

# 4) Upgrade installer tooling
python -m pip install --upgrade pip setuptools wheel

# 5) Install dependencies with safe version ranges
# Try requirements.txt first (provided below). If you don't have it yet, skip to the "Requirements file" section.
python -m pip install -r requirements.txt

# If you hit conflicts, install core libs directly:
# python -m pip install "numpy>=1.26,<2.3" "scipy>=1.13,<1.14" pandas flask plotly

# 6) Run the app
python app.py
# Then open: http://127.0.0.1:5000

Quick Start (Conda alternative)

Text:
Use a dedicated Conda env if you prefer. This avoids mixing with base/Anaconda.

Code:

conda deactivate 2>/dev/null || true
conda create -y -n pathoscope python=3.12
conda activate pathoscope

# Install with requirements.txt
python -m pip install -r requirements.txt

# Or install core libs directly if needed:
# python -m pip install "numpy>=1.26,<2.3" "scipy>=1.13,<1.14" pandas flask plotly

python app.py

Requirements file (cross-machine friendly)

Text:
Use ranges instead of strict pins. This resolves the conflict you saw (numpy==2.3.1 vs scipy==1.13.1).

Code (save as requirements.txt):

flask>=3.0
plotly>=5.18
pandas>=2.2
numpy>=1.26,<2.3
scipy>=1.13,<1.14
