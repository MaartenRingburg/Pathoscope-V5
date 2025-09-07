#!/usr/bin/env python3
"""
Simple test to check if Flask sessions are working
"""

import requests
import time

BASE_URL = "http://localhost:5001"

def test_session():
    """Test if sessions are working."""
    print("🔍 Testing Flask session functionality...")
    
    # Create a session
    session = requests.Session()
    
    # Test homepage
    response = session.get(f"{BASE_URL}/")
    print(f"Homepage status: {response.status_code}")
    
    # Submit disease analysis
    data = {"disease_name": "Alzheimer's"}
    response = session.post(f"{BASE_URL}/", data=data, allow_redirects=False)
    print(f"POST status: {response.status_code}")
    print(f"Location header: {response.headers.get('Location', 'None')}")
    
    # Check results page with same session
    response = session.get(f"{BASE_URL}/results")
    print(f"Results status: {response.status_code}")
    
    # Check if we got the results page or redirect
    if "Redirecting" in response.text:
        print("❌ Session not working - got redirect")
        return False
    else:
        print("✅ Session working - got results page")
        print("Content preview:")
        print(response.text[:500])
        return True

if __name__ == "__main__":
    test_session() 