from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from celery import Celery
from config import Config

# Init Flask
app = Flask(
    __name__,
    static_folder='../frontend/build',
    template_folder='../frontend/build'
)
app.config.from_object(Config)

# Firebase Auth
from modules.auth import init_firebase, login_required
init_firebase(app)

# Celery
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(result_backend=app.config['CELERY_RESULT_BACKEND'])

# History Storage
from modules.utils import init_history, load_history, save_history, delete_history_item, generate_pdf
init_history()

# Analysis Modules
from modules.analysis import analyze_disease
from modules.enrichment import run_enrichment
from modules.kegg_api import fetch_kegg_pathways, kegg_pathway_image_url
from modules.string_api import fetch_string_network
from modules.ai_driver import get_gemini_explanation
from modules.drugbank import get_drug_targets

# Serve React App
@app.route('/', defaults={'path': ''})
def serve_react(path):
    return app.send_static_file('index.html')

# API: History
@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    return jsonify(load_history())

@app.route('/api/history/<int:i>', methods=['DELETE'])
@login_required
def api_delete_history(i):
    delete_history_item(i)
    return '', 204

# API: Start Analysis
@app.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    disease = request.form.get('disease_name', '')
    csv_file = request.files.get('csv_file')
    data = csv_file.read() if csv_file else None
    job = analyze_async.delay(disease, data)
    return jsonify({'job_id': job.id}), 202

# API: Poll Results
@app.route('/api/results/<job_id>', methods=['GET'])
@login_required
def api_get_results(job_id):
    res = celery.AsyncResult(job_id)
    if not res.ready():
        return jsonify({'status': 'pending'}), 202
    return jsonify(res.get())

# API: Download PDF
@app.route('/api/download_pdf/<job_id>', methods=['GET'])
@login_required
def api_download_pdf(job_id):
    result = celery.AsyncResult(job_id).get()
    pdf_path = generate_pdf(result)
    return send_file(pdf_path, as_attachment=True)

# Celery Task: Full Pipeline
@celery.task(bind=True)
def analyze_async(self, disease, csv_bytes):
    import io, pandas as pd
    df = pd.read_csv(io.BytesIO(csv_bytes), index_col=0) if csv_bytes else None

    genes, pathways, volcano_data, df_ref = analyze_disease(df)
    enrichment = run_enrichment(genes)
    kegg_ids = fetch_kegg_pathways(genes)
    kegg_images = [kegg_pathway_image_url(pid) for pid in kegg_ids]
    string_net = fetch_string_network(genes)
    explanation = get_gemini_explanation(disease, genes, pathways)
    drugs = get_drug_targets(genes)

    result = {
        'disease': disease,
        'genes': genes,
        'pathways': pathways,
        'volcano_data': volcano_data,
        'heatmap': {
            'genes': df_ref.index.tolist(),
            'samples': df_ref.columns.tolist(),
            'values': df_ref.values.tolist()
        } if df_ref is not None else None,
        'enrichment': enrichment,
        'kegg_images': kegg_images,
        'string_network': string_net,
        'explanation': explanation,
        'drugs': drugs
    }
    save_history(result)
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)