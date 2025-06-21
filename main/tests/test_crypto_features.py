#!/usr/bin/env python3
"""
Test script for crypto features
This script tests the encryption/decryption functionality and file management
"""

import os
import tempfile
import requests
from core import crypto
from utils.auth_state import set_jwt_token_global

def test_crypto_functionality():
    """Test the crypto functionality"""
    print("Testing crypto functionality...")
    
    # Create a test file
    test_content = "This is a test file for encryption/decryption testing."
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    print(f"Created test file: {test_file_path}")
    
    try:
        # Test encryption (this will prompt for password)
        print("\nTesting encryption...")
        print("Note: You will be prompted for a password")
        crypto.encrypt_file(test_file_path)
        
        # Check if encrypted file was created
        encrypted_path = test_file_path + '.enc'
        if os.path.exists(encrypted_path):
            print(f"✓ Encryption successful: {encrypted_path}")
        else:
            print("✗ Encryption failed: encrypted file not found")
            return
        
        # Test decryption (this will prompt for password)
        print("\nTesting decryption...")
        print("Note: You will be prompted for the same password")
        crypto.decrypt_file(encrypted_path)
        
        # Check if decrypted file was created
        decrypted_path = encrypted_path.replace('.enc', '.dec')
        if os.path.exists(decrypted_path):
            print(f"✓ Decryption successful: {decrypted_path}")
            
            # Verify content
            with open(decrypted_path, 'r') as f:
                decrypted_content = f.read()
            
            if decrypted_content == test_content:
                print("✓ Content verification successful")
            else:
                print("✗ Content verification failed")
        else:
            print("✗ Decryption failed: decrypted file not found")
    
    finally:
        # Cleanup
        for path in [test_file_path, encrypted_path, decrypted_path]:
            if os.path.exists(path):
                os.remove(path)
                print(f"Cleaned up: {path}")

def test_backend_connection():
    """Test connection to backend"""
    print("\nTesting backend connection...")
    
    try:
        response = requests.get('https://127.0.0.1:5000/chrome', verify=False)
        if response.status_code == 200:
            print("✓ Backend connection successful")
            return True
        else:
            print(f"✗ Backend connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Crypto Features Test ===\n")
    
    # Test backend connection first
    if not test_backend_connection():
        print("\nBackend is not running. Please start the backend server first.")
        print("Run: cd backend && python run.py")
        return
    
    # Test crypto functionality
    test_crypto_functionality()
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main() 