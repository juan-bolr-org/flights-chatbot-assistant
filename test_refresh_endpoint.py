#!/usr/bin/env python3
"""
Quick test script to demonstrate the new refresh token endpoint.
This script simulates the workflow of:
1. User registration
2. Token refresh
3. Logout
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/users"

def test_refresh_endpoint():
    """Test the refresh token endpoint workflow."""
    
    # Test data
    user_data = {
        "name": "Test User",
        "email": "test.refresh@example.com",
        "password": "secure_password123",
        "phone": "+1234567890"
    }
    
    login_data = {
        "email": "test.refresh@example.com",
        "password": "secure_password123"
    }
    
    print("🚀 Testing Token Refresh Endpoint")
    print("=" * 50)
    
    # Step 1: Register user (or login if already exists)
    print("1. Registering/Logging in user...")
    
    # Try to register first
    try:
        response = requests.post(f"{API_BASE}/register", json=user_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
            data = response.json()
            original_token = data["access_token"]
        else:
            # User might already exist, try login
            response = requests.post(f"{API_BASE}/login", json=login_data)
            if response.status_code == 200:
                print("✅ User logged in successfully")
                data = response.json()
                original_token = data["token"]["access_token"]
            else:
                print(f"❌ Failed to register/login: {response.status_code}")
                print(response.text)
                return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the API. Make sure the server is running at http://localhost:8000")
        return
    
    print(f"   Original token (first 20 chars): {original_token[:20]}...")
    
    # Step 2: Test refresh token endpoint
    print("\n2. Testing token refresh...")
    
    headers = {
        "Authorization": f"Bearer {original_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{API_BASE}/refresh", headers=headers)
        
        if response.status_code == 200:
            print("✅ Token refreshed successfully!")
            refresh_data = response.json()
            new_token = refresh_data["access_token"]
            print(f"   New token (first 20 chars): {new_token[:20]}...")
            print(f"   Token type: {refresh_data['token_type']}")
            
            # Verify tokens are different
            if new_token != original_token:
                print("✅ New token is different from original (as expected)")
            else:
                print("⚠️  New token is the same as original (unexpected)")
                
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(response.text)
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return
    
    # Step 3: Test that new token works
    print("\n3. Testing new token with /me endpoint...")
    
    new_headers = {
        "Authorization": f"Bearer {new_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{API_BASE}/me", headers=new_headers)
        
        if response.status_code == 200:
            print("✅ New token works correctly!")
            user_info = response.json()
            print(f"   User: {user_info['name']} ({user_info['email']})")
        else:
            print(f"❌ New token doesn't work: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Step 4: Test logout
    print("\n4. Testing logout...")
    
    try:
        response = requests.post(f"{API_BASE}/logout")
        
        if response.status_code == 200:
            print("✅ Logout successful!")
            logout_data = response.json()
            print(f"   Message: {logout_data['message']}")
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    print("\nNote: The refresh endpoint creates a token with 30 minutes duration")
    print("and sets it as an HTTP-only cookie with the same duration.")

if __name__ == "__main__":
    test_refresh_endpoint()
