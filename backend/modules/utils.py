# backend/modules/utils.py
import os
import json
from reportlab.pdfgen import canvas

HISTORY_FILE = "history.json"

def init_history():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

def load_history():
    try:
        return json.load(open(HISTORY_FILE))
    except Exception:
        return []

def save_history(entry):
    h = load_history()
    h.insert(0, entry)
    json.dump(h, open(HISTORY_FILE, 'w'))

def delete_history_item(i):
    h = load_history()
    if 0 <= i < len(h):
        h.pop(i)
        json.dump(h, open(HISTORY_FILE, 'w'))

def generate_pdf(r):
    """
    Generate a simple PDF report from result dict.
    """
    path = "report.pdf"
    c = canvas.Canvas(path)
    c.drawString(100, 800, f"Disease: {r.get('disease', 'Unknown')}")
    c.drawString(100, 780, f"Genes: {', '.join(r.get('genes', [])[:5])}")
    c.drawString(100, 760, f"Pathways: {', '.join(r.get('pathways', [])[:5])}")
    c.drawString(100, 740, f"Drugs: {', '.join(r.get('drugs', [])[:5])}")
    if 'enrichment' in r and r['enrichment']:
        c.drawString(100, 720, f"Enrichment: {', '.join([str(t[0]) for t in r['enrichment'][:5]])}")
    c.drawString(100, 700, f"Explanation: {r.get('explanation', 'No explanation available.')[:200]}...")
    c.save()
    return path