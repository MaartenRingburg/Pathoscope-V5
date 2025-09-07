# backend/modules/string_api.py
import requests

def fetch_string_network(genes, species=9606):
    """
    Fetch protein-protein interaction network from STRING-DB.
    Returns JSON edges with stringId_A, stringId_B, score.
    """
    if not genes:
        return []
    # join up to 20 gene identifiers
    ids = "%0D".join(genes[:20])
    url = f"https://string-db.org/api/json/network?identifiers={ids}&species={species}"
    r = requests.get(url)
    return r.json() if r.ok else []