#!/usr/bin/env python3
"""
Simple test script to demonstrate the Smart Content Moderator API functionality.
Run this after starting the API server.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_text_moderation():
    """Test text moderation endpoint."""
    print("📝 Testing text moderation...")
    
    # Test safe content
    safe_text = {
        "email": "test@example.com",
        "text": "Hello, this is a friendly message about technology and innovation."
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/moderate/text", json=safe_text)
    print(f"Safe text - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test potentially toxic content
    toxic_text = {
        "email": "test@example.com",
        "text": "This is a test message with potentially offensive language."
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/moderate/text", json=toxic_text)
    print(f"Toxic text - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_image_moderation():
    """Test image moderation endpoint."""
    print("🖼️ Testing image moderation...")
    
    # Test with a public image URL
    image_request = {
        "email": "test@example.com",
        "image_url": "https://picsum.photos/400/300"  # Random placeholder image
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/moderate/image", json=image_request)
    print(f"Image moderation - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_analytics():
    """Test analytics endpoints."""
    print("📊 Testing analytics...")
    
    # Test user analytics
    response = requests.get(f"{BASE_URL}/api/v1/analytics/summary?user=test@example.com")
    print(f"User analytics - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Test all users analytics
    response = requests.get(f"{BASE_URL}/api/v1/analytics/summary/all")
    print(f"All users analytics - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_error_handling():
    """Test error handling."""
    print("⚠️ Testing error handling...")
    
    # Test invalid request
    invalid_request = {
        "email": "invalid-email",
        "text": ""
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/moderate/text", json=invalid_request)
    print(f"Invalid request - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests."""
    print("🚀 Smart Content Moderator API Test Suite")
    print("=" * 50)
    
    try:
        # Test health check first
        test_health_check()
        
        # Wait a moment for any startup processes
        time.sleep(2)
        
        # Test text moderation
        test_text_moderation()
        
        # Test image moderation
        test_image_moderation()
        
        # Test analytics
        test_analytics()
        
        # Test error handling
        test_error_handling()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    main()



