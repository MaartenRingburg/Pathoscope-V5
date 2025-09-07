# modules/kegg_api.py

import requests

KEGG_DISEASE_SEARCH = "http://rest.kegg.jp/find/disease/{}"
KEGG_DISEASE_LINK   = "http://rest.kegg.jp/link/hsa/{}"
KEGG_PATHWAY_IMG    = "http://rest.kegg.jp/get/{}/image"

# Common disease name mappings for KEGG
DISEASE_MAPPINGS = {
    "alzheimer": "alzheimer",
    "alzheimer's": "alzheimer",
    "alzheimer's disease": "alzheimer",
    "diabetes": "diabetes",
    "diabetes mellitus": "diabetes",
    "cancer": "cancer",
    "breast cancer": "breast cancer",
    "lung cancer": "lung cancer",
    "parkinson": "parkinson",
    "parkinson's": "parkinson",
    "parkinson's disease": "parkinson",
    "hypertension": "hypertension",
    "asthma": "asthma",
    "arthritis": "arthritis",
    "rheumatoid arthritis": "rheumatoid arthritis",
    "obesity": "obesity",
    "depression": "depression",
    "schizophrenia": "schizophrenia",
    "autism": "autism",
    "epilepsy": "epilepsy"
}

# Fallback genes for common diseases when KEGG search fails
FALLBACK_GENES = {
    "alzheimer": ["APP", "PSEN1", "PSEN2", "APOE", "MAPT", "SNCA", "GRN", "VCP", "CHMP2B", "TARDBP"],
    "alzheimer's": ["APP", "PSEN1", "PSEN2", "APOE", "MAPT", "SNCA", "GRN", "VCP", "CHMP2B", "TARDBP"],
    "alzheimer's disease": ["APP", "PSEN1", "PSEN2", "APOE", "MAPT", "SNCA", "GRN", "VCP", "CHMP2B", "TARDBP"],
    "diabetes": ["INS", "INSR", "GCK", "HNF1A", "HNF4A", "PPARG", "KCNJ11", "ABCC8", "MTTP", "WFS1"],
    "diabetes mellitus": ["INS", "INSR", "GCK", "HNF1A", "HNF4A", "PPARG", "KCNJ11", "ABCC8", "MTTP", "WFS1"],
    "cancer": ["TP53", "BRCA1", "BRCA2", "APC", "KRAS", "PIK3CA", "PTEN", "CDKN2A", "RB1", "MYC"],
    "breast cancer": ["BRCA1", "BRCA2", "TP53", "PTEN", "CDH1", "STK11", "PALB2", "CHEK2", "ATM", "BARD1"],
    "lung cancer": ["EGFR", "KRAS", "ALK", "ROS1", "BRAF", "MET", "RET", "TP53", "CDKN2A", "PTEN"],
    "parkinson": ["SNCA", "LRRK2", "PARK2", "PINK1", "DJ1", "ATP13A2", "VPS35", "EIF4G1", "DNAJC6", "SYNJ1"],
    "parkinson's": ["SNCA", "LRRK2", "PARK2", "PINK1", "DJ1", "ATP13A2", "VPS35", "EIF4G1", "DNAJC6", "SYNJ1"],
    "parkinson's disease": ["SNCA", "LRRK2", "PARK2", "PINK1", "DJ1", "ATP13A2", "VPS35", "EIF4G1", "DNAJC6", "SYNJ1"],
    "hypertension": ["ACE", "AGT", "AGTR1", "CYP11B2", "ADD1", "GNB3", "NOS3", "EDN1", "EDNRA", "EDNRB"],
    "asthma": ["IL13", "IL4", "IL5", "TNF", "ADAM33", "GSDMB", "ORMDL3", "CHI3L1", "HLA-DQB1", "IL33"],
    "arthritis": ["TNF", "IL1B", "IL6", "IL17A", "IL23R", "PTPN22", "CTLA4", "STAT4", "TRAF1", "CD40"],
    "rheumatoid arthritis": ["TNF", "IL1B", "IL6", "IL17A", "IL23R", "PTPN22", "CTLA4", "STAT4", "TRAF1", "CD40"],
    "obesity": ["LEP", "LEPR", "MC4R", "POMC", "FTO", "TMEM18", "GNPDA2", "SH2B1", "MTCH2", "NEGR1"],
    "depression": ["SLC6A4", "COMT", "MAOA", "BDNF", "HTR2A", "DRD2", "DRD4", "TPH2", "GABRA2", "CRHR1"],
    "schizophrenia": ["DISC1", "COMT", "DRD2", "HTR2A", "BDNF", "NRG1", "DTNBP1", "DAOA", "G72", "CHRNA7"],
    "autism": ["SHANK3", "CHD8", "ADNP", "ARID1B", "DYRK1A", "GRIN2B", "MECP2", "FOXP1", "FOXP2", "CNTNAP2"],
    "epilepsy": ["SCN1A", "SCN2A", "KCNQ2", "KCNQ3", "GABRA1", "GABRG2", "CHRNA4", "CHRNB2", "LGI1", "DEPDC5"]
}

# Fallback pathways for common diseases
FALLBACK_PATHWAYS = {
    "alzheimer": ["hsa05010", "hsa05012", "hsa05014", "hsa05016", "hsa05020"],
    "alzheimer's": ["hsa05010", "hsa05012", "hsa05014", "hsa05016", "hsa05020"],
    "alzheimer's disease": ["hsa05010", "hsa05012", "hsa05014", "hsa05016", "hsa05020"],
    "diabetes": ["hsa04910", "hsa04930", "hsa04931", "hsa04932", "hsa04940"],
    "diabetes mellitus": ["hsa04910", "hsa04930", "hsa04931", "hsa04932", "hsa04940"],
    "cancer": ["hsa05200", "hsa05202", "hsa05203", "hsa05204", "hsa05205"],
    "breast cancer": ["hsa05224", "hsa05215", "hsa05216", "hsa05217", "hsa05218"],
    "lung cancer": ["hsa05223", "hsa05215", "hsa05216", "hsa05217", "hsa05218"],
    "parkinson": ["hsa05012", "hsa05014", "hsa05016", "hsa05020", "hsa05022"],
    "parkinson's": ["hsa05012", "hsa05014", "hsa05016", "hsa05020", "hsa05022"],
    "parkinson's disease": ["hsa05012", "hsa05014", "hsa05016", "hsa05020", "hsa05022"],
    "hypertension": ["hsa04924", "hsa04925", "hsa04926", "hsa04927", "hsa04928"],
    "asthma": ["hsa05310", "hsa05320", "hsa05321", "hsa05322", "hsa05323"],
    "arthritis": ["hsa05323", "hsa05322", "hsa05321", "hsa05320", "hsa05310"],
    "rheumatoid arthritis": ["hsa05323", "hsa05322", "hsa05321", "hsa05320", "hsa05310"],
    "obesity": ["hsa04931", "hsa04932", "hsa04933", "hsa04934", "hsa04935"],
    "depression": ["hsa04726", "hsa04727", "hsa04728", "hsa04729", "hsa04730"],
    "schizophrenia": ["hsa04726", "hsa04727", "hsa04728", "hsa04729", "hsa04730"],
    "autism": ["hsa04726", "hsa04727", "hsa04728", "hsa04729", "hsa04730"],
    "epilepsy": ["hsa04726", "hsa04727", "hsa04728", "hsa04729", "hsa04730"]
}

def fetch_kegg_genes(disease_name, max_genes=10):
    """Given a disease name (e.g. "Alzheimer"), returns up to max_genes KEGG human gene IDs."""
    try:
        # Try different variations of the disease name
        search_terms = [disease_name.lower()]
        
        # Add mapped variations
        if disease_name.lower() in DISEASE_MAPPINGS:
            search_terms.append(DISEASE_MAPPINGS[disease_name.lower()])
        
        # Add common variations
        if "alzheimer" in disease_name.lower():
            search_terms.extend(["alzheimer", "alzheimer disease"])
        elif "diabetes" in disease_name.lower():
            search_terms.extend(["diabetes", "diabetes mellitus"])
        elif "cancer" in disease_name.lower():
            search_terms.extend(["cancer", "tumor"])
        elif "parkinson" in disease_name.lower():
            search_terms.extend(["parkinson", "parkinson disease"])
        
        # Try each search term
        for search_term in search_terms:
            print(f"Searching KEGG for: {search_term}")
            r = requests.get(KEGG_DISEASE_SEARCH.format(search_term), timeout=10)
            if not r.ok or not r.text:
                continue
                
            lines = r.text.splitlines()
            if not lines:
                continue
            
            # Parse the first line more safely
            first_line = lines[0]
            if '\t' not in first_line:
                continue
            
            parts = first_line.split("\t")
            if len(parts) < 1:
                continue
                
            entry_part = parts[0]
            if ':' not in entry_part:
                continue
                
            entry = entry_part.split(":")[1]
            r2 = requests.get(KEGG_DISEASE_LINK.format(entry), timeout=10)
            if not r2.ok or not r2.text:
                continue
                
            genes = []
            for line in r2.text.splitlines():
                if '\t' in line and ':' in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        gene_part = parts[1]
                        if ':' in gene_part:
                            gene_id = gene_part.split(":")[1]
                            genes.append(gene_id)
            
            if genes:
                print(f"Found {len(genes)} genes for {search_term}")
                return genes[:max_genes]
        
        print(f"No genes found for disease: {disease_name}")
        
        # Try fallback genes
        disease_lower = disease_name.lower()
        for key in FALLBACK_GENES:
            if key in disease_lower or disease_lower in key:
                print(f"Using fallback genes for: {key}")
                return FALLBACK_GENES[key][:max_genes]
        
        # If no fallback found, return some general genes
        print("Using general fallback genes")
        return ["TP53", "BRCA1", "APOE", "INS", "TNF"][:max_genes]
        
    except Exception as e:
        print(f"Error fetching KEGG genes: {e}")
        return []


def get_fallback_pathways(disease_name, max_paths=5):
    """Get fallback pathways for a specific disease."""
    disease_lower = disease_name.lower()
    for key in FALLBACK_PATHWAYS:
        if key in disease_lower or disease_lower in key:
            print(f"Using fallback pathways for: {key}")
            return FALLBACK_PATHWAYS[key][:max_paths]
    return ["hsa00010", "hsa00020", "hsa00030", "hsa00040", "hsa00051"][:max_paths]

def fetch_kegg_pathways(genes, max_paths=5, disease_name=None):
    """Given a list of KEGG gene IDs, returns up to max_paths pathway IDs."""
    try:
        pathways = []
        for g in genes:
            r = requests.get(f"http://rest.kegg.jp/link/pathway/hsa:{g}", timeout=10)
            if not r.ok or not r.text:
                continue
            for line in r.text.splitlines():
                if '\t' in line and ':' in line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        pathway_part = parts[1]
                        if ':' in pathway_part:
                            pid = pathway_part.split(":")[1]
                            if pid not in pathways:
                                pathways.append(pid)
                            if len(pathways) >= max_paths:
                                return pathways
        
        # If no pathways found from genes, try disease-specific fallback
        if not pathways and disease_name:
            return get_fallback_pathways(disease_name, max_paths)
        elif not pathways:
            print("No pathways found from genes, using general fallback pathways")
            return ["hsa00010", "hsa00020", "hsa00030", "hsa00040", "hsa00051"][:max_paths]
        
        return pathways
    except Exception as e:
        print(f"Error fetching KEGG pathways: {e}")
        # Return disease-specific fallback pathways on error
        if disease_name:
            return get_fallback_pathways(disease_name, max_paths)
        return ["hsa00010", "hsa00020", "hsa00030", "hsa00040", "hsa00051"][:max_paths]


def kegg_pathway_image_url(pathway_id):
    """Returns the KEGG pathway diagram URL for embedding."""
    return KEGG_PATHWAY_IMG.format(pathway_id)