# PathoScope V5


PathoScope V5 is a bioinformatics platform designed to integrate gene expression analysis, pathway visualization, and AI-driven drug–target predictions.  
It provides an accessible environment for researchers, students, and professionals to explore disease mechanisms and therapeutic targets.

---

## Features

- Upload and analyze gene expression datasets (CSV/TSV).
- Visualize KEGG pathways with integrated differential expression mapping.
- Predict drug–target interactions using DrugBank and AI models.
- Export results as publication-ready PDF reports.
- User account system with local and Firebase storage support.
- Responsive interface with adaptive light/dark theme.

---

## Technology Stack

- **Backend:** Python (Flask)  
- **Frontend:** HTML, CSS, JavaScript  
- **Visualization:** Plotly, Cytoscape.js  
- **Database/Storage:** Local and Firebase  
- **APIs:** DrugBank, KEGG  
- **Export:** ReportLab (PDF generation)

---

## Installation

Clone the repository:
```bash
git clone https://github.com/Acr0matix/Pathoscope-V5.git
cd Pathoscope-V5

Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

Run the application locally:

flask run


Open the browser at:

http://127.0.0.1:5000/
