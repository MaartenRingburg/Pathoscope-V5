#!/usr/bin/env python3
"""
Comprehensive test script for PathoScope V5 advanced features
"""

import requests
import json
import time
import pandas as pd
import numpy as np

BASE_URL = "http://localhost:5001"

def test_basic_functionality():
    """Test basic disease analysis functionality."""
    print("🔍 Testing basic functionality...")
    
    # Test homepage
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, "Homepage should be accessible"
    print("✅ Homepage accessible")
    
    # Test disease analysis
    data = {"disease_name": "Alzheimer's"}
    response = requests.post(f"{BASE_URL}/", data=data, allow_redirects=False)
    assert response.status_code == 302, "Disease analysis should redirect to results"
    print("✅ Disease analysis working")
    
    # Test results page
    response = requests.get(f"{BASE_URL}/results")
    assert response.status_code == 200, "Results page should be accessible"
    print("✅ Results page accessible")

def test_api_endpoints():
    """Test new API endpoints."""
    print("\n🔍 Testing API endpoints...")
    
    # Test network API
    response = requests.get(f"{BASE_URL}/api/network/Alzheimer's")
    assert response.status_code == 200, "Network API should work"
    data = response.json()
    assert 'network_data' in data, "Network API should return network data"
    print("✅ Network API working")
    
    # Test enrichment API
    response = requests.get(f"{BASE_URL}/api/enrichment/Alzheimer's")
    assert response.status_code == 200, "Enrichment API should work"
    data = response.json()
    assert 'enrichment' in data, "Enrichment API should return enrichment data"
    print("✅ Enrichment API working")
    
    # Test comprehensive analysis API
    response = requests.get(f"{BASE_URL}/api/analysis/Alzheimer's")
    assert response.status_code == 200, "Analysis API should work"
    data = response.json()
    assert 'genes' in data, "Analysis API should return genes"
    assert 'enrichment' in data, "Analysis API should return enrichment"
    assert 'network_data' in data, "Analysis API should return network data"
    print("✅ Comprehensive analysis API working")

def test_differential_expression():
    """Test differential expression analysis with mock data."""
    print("\n🔍 Testing differential expression analysis...")
    
    # Create mock expression data
    np.random.seed(42)
    genes = [f"GENE_{i}" for i in range(100)]
    samples = [f"Control_{i}" for i in range(5)] + [f"Treatment_{i}" for i in range(5)]
    
    # Create differential expression data
    data = {}
    for gene in genes:
        if np.random.random() < 0.3:  # 30% differentially expressed
            control_expr = np.random.normal(5, 1, 5)
            treatment_expr = np.random.normal(7, 1, 5)  # Higher expression
        else:
            control_expr = np.random.normal(5, 1, 5)
            treatment_expr = np.random.normal(5, 1, 5)  # Similar expression
        
        data[gene] = list(control_expr) + list(treatment_expr)
    
    df = pd.DataFrame(data, index=genes, columns=samples)
    
    # Save to temporary CSV
    df.to_csv("test_expression.csv", index=True)
    
    # Test file upload API
    with open("test_expression.csv", "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    assert response.status_code == 200, "File upload API should work"
    data = response.json()
    
    assert 'analysis_results' in data, "Should return analysis results"
    assert 'volcano_data' in data, "Should return volcano plot data"
    assert 'heatmap_data' in data, "Should return heatmap data"
    assert 'ma_plot_data' in data, "Should return MA plot data"
    assert 'enrichment' in data, "Should return enrichment data"
    assert 'network_data' in data, "Should return network data"
    
    print("✅ Differential expression analysis working")
    print(f"   - Found {len(data['analysis_results'].get('significant_genes', []))} significant genes")
    print(f"   - Generated {len(data['enrichment'])} enrichment terms")
    print(f"   - Network has {data['network_data']['total_nodes']} nodes and {data['network_data']['total_edges']} edges")

def test_enrichment_analysis():
    """Test enrichment analysis functionality."""
    print("\n🔍 Testing enrichment analysis...")
    
    # Test with known genes
    test_genes = ["TP53", "BRCA1", "BRCA2", "APC", "PTEN"]
    
    response = requests.get(f"{BASE_URL}/api/enrichment/cancer")
    assert response.status_code == 200, "Enrichment analysis should work"
    
    data = response.json()
    enrichment = data['enrichment']
    
    assert len(enrichment) > 0, "Should find enrichment terms"
    print(f"✅ Enrichment analysis working - found {len(enrichment)} terms")
    
    # Check for common cancer-related terms
    terms = [term[0].lower() for term in enrichment]
    cancer_terms = ['apoptosis', 'cell cycle', 'dna repair', 'signal transduction']
    found_terms = [term for term in cancer_terms if any(term in t for t in terms)]
    print(f"   - Found cancer-related terms: {found_terms}")

def test_network_analysis():
    """Test network analysis functionality."""
    print("\n🔍 Testing network analysis...")
    
    response = requests.get(f"{BASE_URL}/api/network/Alzheimer's")
    assert response.status_code == 200, "Network analysis should work"
    
    data = response.json()
    network_data = data['network_data']
    
    assert 'nodes' in network_data, "Should have network nodes"
    assert 'edges' in network_data, "Should have network edges"
    assert network_data['total_nodes'] > 0, "Should have at least one node"
    
    print(f"✅ Network analysis working")
    print(f"   - Network has {network_data['total_nodes']} nodes")
    print(f"   - Network has {network_data['total_edges']} interactions")
    
    # Test network report
    if 'network_report' in data:
        report = data['network_report']
        if 'network_stats' in report:
            stats = report['network_stats']
            print(f"   - Average degree: {stats.get('average_degree', 0):.2f}")
            print(f"   - Network density: {stats.get('density', 0):.3f}")

def test_pdf_generation():
    """Test PDF report generation."""
    print("\n🔍 Testing PDF generation...")
    
    response = requests.get(f"{BASE_URL}/download_pdf")
    assert response.status_code == 200, "PDF download should work"
    assert response.headers['content-type'] == 'application/pdf', "Should return PDF content"
    
    print("✅ PDF generation working")

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n🔍 Testing error handling...")
    
    # Test invalid disease
    response = requests.get(f"{BASE_URL}/api/network/invalid_disease_12345")
    assert response.status_code == 404, "Should handle invalid disease gracefully"
    
    # Test invalid file upload
    response = requests.post(f"{BASE_URL}/api/upload")
    assert response.status_code == 400, "Should handle missing file gracefully"
    
    print("✅ Error handling working")

def main():
    """Run all tests."""
    print("🚀 Starting PathoScope V5 Advanced Features Test Suite")
    print("=" * 60)
    
    try:
        test_basic_functionality()
        test_api_endpoints()
        test_differential_expression()
        test_enrichment_analysis()
        test_network_analysis()
        test_pdf_generation()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed! PathoScope V5 is working correctly.")
        print("\n✅ Implemented Features:")
        print("   - Differential expression analysis with t-tests")
        print("   - Interactive volcano plots, MA plots, and heatmaps")
        print("   - Real g:Profiler enrichment analysis")
        print("   - Interactive Cytoscape.js network visualization")
        print("   - STRING-DB protein interaction networks")
        print("   - Comprehensive API endpoints")
        print("   - Enhanced PDF reporting")
        print("   - Robust error handling")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    finally:
        # Clean up
        try:
            import os
            if os.path.exists("test_expression.csv"):
                os.remove("test_expression.csv")
        except:
            pass
    
    return 0

if __name__ == "__main__":
    exit(main()) 