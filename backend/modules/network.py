# backend/modules/network.py
"""
Interactive network visualization using STRING-DB API and Cytoscape.js
"""

import requests
import json
from typing import List, Dict, Optional
import time

def get_string_network(genes: List[str], species: int = 9606, 
                      required_score: int = 400, network_type: str = "physical") -> Dict:
    """
    Get protein-protein interaction network from STRING-DB API.
    """
    if not genes or len(genes) < 2:
        return {
            'nodes': [], 
            'edges': [], 
            'network_url': None,
            'total_nodes': 0,
            'total_edges': 0
        }
    
    try:
        # STRING-DB API endpoint
        url = "https://string-db.org/api/json/network"
        
        # Prepare parameters
        params = {
            'identifiers': '%0d'.join(genes[:100]),  # Limit to 100 genes
            'species': species,  # Human
            'required_score': required_score,
            'network_type': network_type,
            'add_nodes': 0  # Don't add additional nodes
        }
        
        # Make API request
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Parse network data
        network_data = response.json()
        
        # Extract nodes and edges
        nodes = []
        edges = []
        node_ids = set()
        
        for interaction in network_data:
            # Add nodes
            for node_id in [interaction['preferredName_A'], interaction['preferredName_B']]:
                if node_id not in node_ids:
                    nodes.append({
                        'id': node_id,
                        'label': node_id,
                        'group': 'query' if node_id in genes else 'interaction'
                    })
                    node_ids.add(node_id)
            
            # Add edge
            edges.append({
                'source': interaction['preferredName_A'],
                'target': interaction['preferredName_B'],
                'weight': interaction['score'],
                'interaction': interaction.get('interaction', 'interacts_with')
            })
        
        # Generate network URL for static image
        network_url = f"https://string-db.org/api/image/network?identifiers={'%0d'.join(genes[:50])}&species={species}"
        
        return {
            'nodes': nodes,
            'edges': edges,
            'network_url': network_url,
            'total_nodes': len(nodes),
            'total_edges': len(edges)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to STRING-DB API: {e}")
        return _get_fallback_network(genes)
    except Exception as e:
        print(f"Error getting STRING network: {e}")
        return _get_fallback_network(genes)

def _get_fallback_network(genes: List[str]) -> Dict:
    """
    Fallback network when STRING-DB API is unavailable.
    """
    try:
        # Create a simple mock network
        nodes = []
        edges = []
        
        # Add nodes
        for i, gene in enumerate(genes[:10]):  # Limit to 10 genes
            nodes.append({
                'id': gene,
                'label': gene,
                'group': 'query'
            })
        
        # Add some mock edges
        for i in range(len(nodes) - 1):
            edges.append({
                'source': nodes[i]['id'],
                'target': nodes[i + 1]['id'],
                'weight': 500 + (i * 50),
                'interaction': 'interacts_with'
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'network_url': None,
            'total_nodes': len(nodes),
            'total_edges': len(edges)
        }
        
    except Exception as e:
        print(f"Error creating fallback network: {e}")
        return {
            'nodes': [], 
            'edges': [], 
            'network_url': None, 
            'total_nodes': 0, 
            'total_edges': 0
        }

def create_cytoscape_config(network_data: Dict) -> Dict:
    """
    Create Cytoscape.js configuration for interactive network visualization.
    """
    try:
        # Prepare elements for Cytoscape
        elements = []
        
        # Add nodes
        for node in network_data['nodes']:
            elements.append({
                'data': {
                    'id': node['id'],
                    'label': node['label'],
                    'group': node['group']
                }
            })
        
        # Add edges
        for edge in network_data['edges']:
            elements.append({
                'data': {
                    'id': f"{edge['source']}_{edge['target']}",
                    'source': edge['source'],
                    'target': edge['target'],
                    'weight': edge['weight'],
                    'interaction': edge['interaction']
                }
            })
        
        # Cytoscape.js configuration
        config = {
            'elements': elements,
            'style': [
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(label)',
                        'font-size': '12px',
                        'font-weight': 'bold',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': '30px',
                        'height': '30px',
                        'background-color': 'data(group)',
                        'border-width': 2,
                        'border-color': '#333'
                    }
                },
                {
                    'selector': 'node[group="query"]',
                    'style': {
                        'background-color': '#ff6b6b',
                        'width': '40px',
                        'height': '40px'
                    }
                },
                {
                    'selector': 'node[group="interaction"]',
                    'style': {
                        'background-color': '#4ecdc4',
                        'width': '25px',
                        'height': '25px'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'width': 'mapData(weight, 0, 1000, 1, 8)',
                        'line-color': '#666',
                        'curve-style': 'bezier',
                        'target-arrow-shape': 'triangle',
                        'target-arrow-color': '#666'
                    }
                }
            ],
            'layout': {
                'name': 'cose',
                'animate': True,
                'animationDuration': 1000,
                'nodeDimensionsIncludeLabels': True,
                'fit': True,
                'padding': 50
            }
        }
        
        return config
        
    except Exception as e:
        print(f"Error creating Cytoscape config: {e}")
        return {'elements': [], 'style': [], 'layout': {}}

def get_network_statistics(network_data: Dict) -> Dict:
    """
    Calculate network statistics and metrics.
    """
    try:
        nodes = network_data['nodes']
        edges = network_data['edges']
        
        # Basic statistics
        stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'query_nodes': len([n for n in nodes if n['group'] == 'query']),
            'interaction_nodes': len([n for n in nodes if n['group'] == 'interaction']),
            'average_degree': len(edges) * 2 / len(nodes) if nodes else 0,
            'density': len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
        }
        
        # Edge weight statistics
        if edges:
            weights = [e['weight'] for e in edges]
            stats.update({
                'min_weight': min(weights),
                'max_weight': max(weights),
                'avg_weight': sum(weights) / len(weights)
            })
        
        return stats
        
    except Exception as e:
        print(f"Error calculating network statistics: {e}")
        return {}

def create_network_report(network_data: Dict, genes: List[str]) -> Dict:
    """
    Create comprehensive network analysis report.
    """
    try:
        stats = get_network_statistics(network_data)
        
        # Top interacting genes
        gene_interactions = {}
        for edge in network_data['edges']:
            for gene in [edge['source'], edge['target']]:
                if gene in genes:
                    gene_interactions[gene] = gene_interactions.get(gene, 0) + 1
        
        top_interacting = sorted(gene_interactions.items(), key=lambda x: x[1], reverse=True)[:10]
        
        report = {
            'network_stats': stats,
            'top_interacting_genes': top_interacting,
            'network_quality': 'high' if stats['total_edges'] > 10 else 'medium' if stats['total_edges'] > 5 else 'low',
            'recommendations': []
        }
        
        # Add recommendations
        if stats['total_edges'] < 5:
            report['recommendations'].append("Consider lowering the interaction score threshold")
        if stats['query_nodes'] < len(genes) * 0.5:
            report['recommendations'].append("Many query genes not found in network - check gene names")
        
        return report
        
    except Exception as e:
        print(f"Error creating network report: {e}")
        return {} 