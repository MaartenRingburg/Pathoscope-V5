from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from dotenv import load_dotenv
import os, json
from backend.modules.analysis import analyze_disease, differential_expression_analysis, create_volcano_plot, create_heatmap, create_ma_plot
from backend.modules.utils import init_history, save_history, load_history, delete_history_item, generate_pdf
from backend.modules.ai_driver import get_gemini_explanation
from backend.modules.drugbank import get_drug_targets
from backend.modules.kegg_api import fetch_kegg_genes, fetch_kegg_pathways, kegg_pathway_image_url
from backend.modules.enrichment import run_enrichment, create_enrichment_plot
from backend.modules.network import get_string_network, create_cytoscape_config, create_network_report

load_dotenv()  # loads GEMINI_API_KEY from .env

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

# expose Python builtins into Jinja
app.jinja_env.globals.update(enumerate=enumerate)

# Initialize storage
init_history()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            disease = request.form.get("disease_name", "")
            print(f"Processing disease: {disease}")
            
            csv_file = request.files.get("csv_file")
            df = None
            if csv_file and csv_file.filename.endswith(".csv"):
                import pandas as pd
                df = pd.read_csv(csv_file)

            genes, pathways = analyze_disease(df)
            if genes is None and pathways is None:
                print(f"Fetching KEGG data for: {disease}")
                genes    = fetch_kegg_genes(disease, max_genes=10)
                pathways = fetch_kegg_pathways(genes, max_paths=5, disease_name=disease)
                print(f"Found {len(genes)} genes and {len(pathways)} pathways")

            # Run comprehensive analysis if we have expression data
            analysis_results = None
            volcano_data = None
            heatmap_data = None
            ma_plot_data = None
            
            if df is not None and not df.empty:
                # Perform differential expression analysis
                analysis_results = differential_expression_analysis(df)
                
                # Create interactive plots
                volcano_data = create_volcano_plot(analysis_results)
                heatmap_data = create_heatmap(df, analysis_results)
                ma_plot_data = create_ma_plot(analysis_results)
                
                # Use significant genes from analysis
                if analysis_results and analysis_results['significant_genes']:
                    genes = analysis_results['significant_genes']

            # Run enrichment analysis
            print(f"Running enrichment for {len(genes)} genes")
            enrichment = run_enrichment(genes, max_terms=10)
            enrichment_plot = create_enrichment_plot(enrichment)
            
            # Get network analysis
            print(f"Getting network data for {len(genes)} genes")
            network_data = get_string_network(genes)
            cytoscape_config = create_cytoscape_config(network_data)
            network_report = create_network_report(network_data, genes)
            
            explanation = get_gemini_explanation(disease, genes, pathways)
            drugs       = get_drug_targets(genes)

            results = {
                "disease": disease, 
                "genes": genes, 
                "pathways": pathways,
                "explanation": explanation, 
                "drugs": drugs, 
                "enrichment": enrichment,
                "enrichment_plot": enrichment_plot,
                "network_data": network_data,
                "cytoscape_config": cytoscape_config,
                "network_report": network_report,
                "volcano_data": volcano_data,
                "heatmap_data": heatmap_data,
                "ma_plot_data": ma_plot_data,
                "analysis_results": analysis_results
            }
            save_history(results)
            
            # Store only essential data in session to avoid cookie size issues
            session_data = {
                "disease": disease,
                "genes": genes,
                "pathways": pathways,
                "explanation": explanation,
                "drugs": drugs,
                "enrichment": enrichment
            }
            session["last"] = session_data
            print(f"Stored session data: {list(session_data.keys())}")
            
            return redirect(url_for("results"))
        except Exception as e:
            print(f"Error processing form: {e}")
            return render_template("index.html", error=f"Error processing request: {str(e)}", history=load_history())

    history = load_history()
    return render_template("index.html", history=history)

@app.route("/results")
def results():
    try:
        r = session.get("last", {})
        print(f"Session data keys: {list(r.keys()) if r else 'None'}")
        print(f"Disease in session: {r.get('disease', 'None')}")
        
        # If no session data, redirect to home
        if not r or not r.get("disease"):
            print("No session data found, redirecting to home")
            return redirect(url_for("index"))
        
        # Get genes and pathways from session
        genes = r.get("genes", [])
        pathways = r.get("pathways", [])
        print(f"Found {len(genes)} genes and {len(pathways)} pathways in session")
        
        # Generate KEGG pathway images
        kegg_images = []
        if pathways:
            kegg_images = [kegg_pathway_image_url(pid) for pid in pathways]
        
        # Generate STRING network image URL
        string_img = None
        if genes:
            ids = "%0D".join(genes[:10])
            string_img = f"https://string-db.org/api/image/network?identifiers={ids}&species=9606"
        
        # Get network data if we have genes
        network_data = {}
        cytoscape_config = {}
        network_report = {}
        if genes:
            network_data = get_string_network(genes)
            cytoscape_config = create_cytoscape_config(network_data)
            network_report = create_network_report(network_data, genes)
        
        # Get enrichment plot
        enrichment = r.get("enrichment", [])
        enrichment_plot = create_enrichment_plot(enrichment) if enrichment else {}
        
        # Provide empty data for missing fields
        volcano_data = {}
        heatmap_data = {}
        ma_plot_data = {}
        analysis_results = {}
        
        return render_template("results.html", r=r,
                               kegg_images=kegg_images,
                               string_image=string_img,
                               volcano_data=volcano_data,
                               heatmap_data=heatmap_data,
                               enrichment=enrichment,
                               enrichment_plot=enrichment_plot,
                               network_data=network_data,
                               cytoscape_config=cytoscape_config,
                               network_report=network_report,
                               ma_plot_data=ma_plot_data,
                               analysis_results=analysis_results)
    except Exception as e:
        print(f"Error in results route: {e}")
        return redirect(url_for("index"))

@app.route("/download_pdf")
def download_pdf():
    try:
        r = session.get("last")
        if not r:
            return redirect(url_for("index"))
        pdf_path = generate_pdf(r)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return redirect(url_for("index"))

@app.route("/delete/<int:i>")
def delete(i):
    try:
        delete_history_item(i)
    except Exception as e:
        print(f"Error deleting history item: {e}")
    return redirect(url_for("index"))

@app.route("/api/network/<disease>")
def api_network(disease):
    """API endpoint for network data."""
    try:
        # Get genes for the disease
        genes = fetch_kegg_genes(disease, max_genes=20)
        if not genes:
            return jsonify({"error": "No genes found for disease"}), 404
        
        # Get network data
        network_data = get_string_network(genes)
        cytoscape_config = create_cytoscape_config(network_data)
        network_report = create_network_report(network_data, genes)
        
        return jsonify({
            "network_data": network_data,
            "cytoscape_config": cytoscape_config,
            "network_report": network_report
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/enrichment/<disease>")
def api_enrichment(disease):
    """API endpoint for enrichment analysis."""
    try:
        # Get genes for the disease
        genes = fetch_kegg_genes(disease, max_genes=20)
        if not genes:
            return jsonify({"error": "No genes found for disease"}), 404
        
        # Run enrichment analysis
        enrichment = run_enrichment(genes, max_terms=20)
        enrichment_plot = create_enrichment_plot(enrichment)
        
        return jsonify({
            "enrichment": enrichment,
            "enrichment_plot": enrichment_plot
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analysis/<disease>")
def api_analysis(disease):
    """API endpoint for comprehensive analysis."""
    try:
        # Get genes and pathways
        genes = fetch_kegg_genes(disease, max_genes=20)
        pathways = fetch_kegg_pathways(genes, max_paths=5, disease_name=disease)
        
        # Run enrichment
        enrichment = run_enrichment(genes, max_terms=10)
        enrichment_plot = create_enrichment_plot(enrichment)
        
        # Get network data
        network_data = get_string_network(genes)
        cytoscape_config = create_cytoscape_config(network_data)
        network_report = create_network_report(network_data, genes)
        
        # Get AI explanation
        explanation = get_gemini_explanation(disease, genes, pathways)
        
        # Get drug targets
        drugs = get_drug_targets(genes)
        
        return jsonify({
            "disease": disease,
            "genes": genes,
            "pathways": pathways,
            "enrichment": enrichment,
            "enrichment_plot": enrichment_plot,
            "network_data": network_data,
            "cytoscape_config": cytoscape_config,
            "network_report": network_report,
            "explanation": explanation,
            "drugs": drugs
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def api_upload():
    """API endpoint for file upload and analysis."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Only CSV files are supported"}), 400
        
        # Read CSV file
        import pandas as pd
        df = pd.read_csv(file)
        
        # Perform differential expression analysis
        analysis_results = differential_expression_analysis(df)
        
        # Create plots
        volcano_data = create_volcano_plot(analysis_results)
        heatmap_data = create_heatmap(df, analysis_results)
        ma_plot_data = create_ma_plot(analysis_results)
        
        # Get significant genes
        significant_genes = analysis_results.get('significant_genes', [])
        
        # Run additional analyses
        enrichment = run_enrichment(significant_genes, max_terms=10)
        enrichment_plot = create_enrichment_plot(enrichment)
        network_data = get_string_network(significant_genes)
        cytoscape_config = create_cytoscape_config(network_data)
        
        return jsonify({
            "analysis_results": analysis_results,
            "volcano_data": volcano_data,
            "heatmap_data": heatmap_data,
            "ma_plot_data": ma_plot_data,
            "enrichment": enrichment,
            "enrichment_plot": enrichment_plot,
            "network_data": network_data,
            "cytoscape_config": cytoscape_config
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001) 