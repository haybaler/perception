#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.user import db
from src.models.client import Client
from src.models.url_analysis import UrlAnalysis
from src.models.analysis_result import AnalysisResult
from main import app

def create_test_client():
    with app.app_context():
        # Check if test client already exists
        existing_client = Client.find_by_domain('test.example.com')
        if existing_client:
            print("Test client already exists!")
            print(f"Domain: {existing_client.domain}")
            print(f"Email: {existing_client.email}")
            print("To get the API key, you'll need to regenerate it through the API")
            return
        
        # Create new test client
        client = Client(
            domain='test.example.com',
            email='test@example.com',
            organization='Test Organization'
        )
        
        # Generate API key
        api_key = client.generate_api_key()
        
        # Save to database
        db.session.add(client)
        db.session.commit()
        
        print("Test client created successfully!")
        print(f"Client ID: {client.id}")
        print(f"Domain: {client.domain}")
        print(f"Email: {client.email}")
        print(f"Organization: {client.organization}")
        print(f"API Key: {api_key}")
        print("\nYou can now use this API key to test the URL scanner!")

if __name__ == '__main__':
    create_test_client()

