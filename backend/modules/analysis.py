# backend/modules/analysis.py
"""
Comprehensive differential expression analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ttest_ind
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple, Optional

def analyze_disease(df: Optional[pd.DataFrame] = None) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    """
    Analyze disease data with comprehensive differential expression analysis.
    Returns (genes, pathways) or (None, None) if no data.
    """
    if df is None:
        return None, None
    
    try:
        # Perform differential expression analysis
        results = differential_expression_analysis(df)
        
        # Extract significant genes
        significant_genes = results['significant_genes']
        
        # Generate pathway analysis
        pathways = analyze_pathways(significant_genes)
        
        return significant_genes, pathways
        
    except Exception as e:
        print(f"Error in disease analysis: {e}")
        return None, None

def differential_expression_analysis(df: pd.DataFrame) -> Dict:
    """
    Perform comprehensive differential expression analysis.
    """
    try:
        # Assume first half of columns are control, second half are treatment
        n_samples = len(df.columns)
        n_control = n_samples // 2
        
        control_cols = df.columns[:n_control]
        treatment_cols = df.columns[n_control:]
        
        results = {
            'genes': [],
            'log2fc': [],
            'p_values': [],
            'adj_p_values': [],
            'significant': [],
            'significant_genes': []
        }
        
        for gene in df.index:
            control_values = df.loc[gene, control_cols].values
            treatment_values = df.loc[gene, treatment_cols].values
            
            # Calculate log2 fold change
            control_mean = np.mean(control_values)
            treatment_mean = np.mean(treatment_values)
            
            if control_mean > 0:
                log2fc = np.log2(treatment_mean / control_mean)
            else:
                log2fc = 0
            
            # Perform t-test
            try:
                t_stat, p_value = ttest_ind(control_values, treatment_values)
            except:
                p_value = 1.0
            
            results['genes'].append(gene)
            results['log2fc'].append(log2fc)
            results['p_values'].append(p_value)
        
        # Multiple testing correction (Benjamini-Hochberg)
        results['adj_p_values'] = stats.false_discovery_control(results['p_values'])
        
        # Identify significant genes (|log2fc| > 1 and adj_p < 0.05)
        for i, gene in enumerate(results['genes']):
            is_significant = (abs(results['log2fc'][i]) > 1 and 
                            results['adj_p_values'][i] < 0.05)
            results['significant'].append(is_significant)
            
            if is_significant:
                results['significant_genes'].append(gene)
        
        return results
        
    except Exception as e:
        print(f"Error in differential expression analysis: {e}")
        return {'significant_genes': []}

def create_volcano_plot(results: Dict) -> Dict:
    """
    Create interactive volcano plot with Plotly.
    """
    try:
        # Prepare data for plotting
        data = []
        for i, gene in enumerate(results['genes']):
            data.append({
                'gene': gene,
                'log2fc': results['log2fc'][i],
                'p_value': results['p_values'][i],
                'adj_p_value': results['adj_p_values'][i],
                'significant': results['significant'][i],
                'color': 'red' if results['significant'][i] else 'gray'
            })
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=[d['log2fc'] for d in data],
            y=[-np.log10(d['p_value']) for d in data],
            mode='markers',
            marker=dict(
                color=[d['color'] for d in data],
                size=8,
                opacity=0.7
            ),
            text=[d['gene'] for d in data],
            hovertemplate='<b>%{text}</b><br>' +
                         'log2FC: %{x:.3f}<br>' +
                         '-log10(p): %{y:.3f}<br>' +
                         '<extra></extra>',
            name='Genes'
        ))
        
        # Add threshold lines
        fig.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="red",
                     annotation_text="p = 0.05")
        fig.add_vline(x=1, line_dash="dash", line_color="red",
                     annotation_text="log2FC = 1")
        fig.add_vline(x=-1, line_dash="dash", line_color="red",
                     annotation_text="log2FC = -1")
        
        # Update layout
        fig.update_layout(
            title="Volcano Plot - Differential Expression",
            xaxis_title="log₂ Fold Change",
            yaxis_title="-log₁₀(p-value)",
            hovermode='closest',
            showlegend=False
        )
        
        return {
            'plot_data': data,
            'figure': fig.to_dict()
        }
        
    except Exception as e:
        print(f"Error creating volcano plot: {e}")
        return {'plot_data': [], 'figure': {}}

def create_heatmap(df: pd.DataFrame, results: Dict) -> Dict:
    """
    Create interactive expression heatmap with Plotly.
    """
    try:
        # Get top significant genes for heatmap
        significant_data = []
        for i, gene in enumerate(results['genes']):
            if results['significant'][i]:
                significant_data.append({
                    'gene': gene,
                    'log2fc': results['log2fc'][i],
                    'p_value': results['p_values'][i]
                })
        
        # Sort by absolute log2fc
        significant_data.sort(key=lambda x: abs(x['log2fc']), reverse=True)
        top_genes = [d['gene'] for d in significant_data[:50]]  # Top 50 genes
        
        # Prepare heatmap data
        heatmap_df = df.loc[top_genes]
        
        # Create Plotly heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale='RdBu_r',
            zmid=0,
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>' +
                         'Sample: %{x}<br>' +
                         'Expression: %{z:.3f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title="Expression Heatmap - Top Significant Genes",
            xaxis_title="Samples",
            yaxis_title="Genes",
            height=600
        )
        
        return {
            'genes': top_genes,
            'samples': list(heatmap_df.columns),
            'values': heatmap_df.values.tolist(),
            'figure': fig.to_dict()
        }
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        return {'genes': [], 'samples': [], 'values': [], 'figure': {}}

def create_ma_plot(results: Dict) -> Dict:
    """
    Create MA plot (log2FC vs average expression).
    """
    try:
        # Calculate average expression (assuming it's available)
        # For now, use mock data
        avg_expression = np.random.normal(5, 2, len(results['genes']))
        
        data = []
        for i, gene in enumerate(results['genes']):
            data.append({
                'gene': gene,
                'log2fc': results['log2fc'][i],
                'avg_expression': avg_expression[i],
                'significant': results['significant'][i],
                'color': 'red' if results['significant'][i] else 'gray'
            })
        
        # Create Plotly figure
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[d['avg_expression'] for d in data],
            y=[d['log2fc'] for d in data],
            mode='markers',
            marker=dict(
                color=[d['color'] for d in data],
                size=8,
                opacity=0.7
            ),
            text=[d['gene'] for d in data],
            hovertemplate='<b>%{text}</b><br>' +
                         'Avg Expression: %{x:.3f}<br>' +
                         'log2FC: %{y:.3f}<br>' +
                         '<extra></extra>',
            name='Genes'
        ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        
        fig.update_layout(
            title="MA Plot - log2FC vs Average Expression",
            xaxis_title="Average Expression (log2)",
            yaxis_title="log₂ Fold Change",
            hovermode='closest',
            showlegend=False
        )
        
        return {
            'plot_data': data,
            'figure': fig.to_dict()
        }
        
    except Exception as e:
        print(f"Error creating MA plot: {e}")
        return {'plot_data': [], 'figure': {}}

def analyze_pathways(genes: List[str]) -> List[str]:
    """
    Analyze pathways for given genes.
    """
    try:
        # Mock pathway analysis - in real implementation, this would use KEGG API
        common_pathways = [
            "hsa04010",  # MAPK signaling pathway
            "hsa04151",  # PI3K-Akt signaling pathway
            "hsa04215",  # Apoptosis
            "hsa04668",  # TNF signaling pathway
            "hsa04915",  # Estrogen signaling pathway
        ]
        
        return common_pathways[:3]  # Return top 3 pathways
        
    except Exception as e:
        print(f"Error in pathway analysis: {e}")
        return []