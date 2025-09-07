# backend/modules/drugbank.py
# Mock DrugBank API integration for target prediction

def get_drug_targets(genes, top_n=5):
    """
    Return mock predicted drug targets for given gene list.
    """
    return [f"Drug_{g}" for g in genes[:top_n]]