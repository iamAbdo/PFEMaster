#!/usr/bin/env python3
"""
Test script for download functionality
This script tests the file download feature
"""

import requests
import os
import tempfile

def test_backend_connection():
    """Test connection to backend"""
    print("Testing backend connection...")
    
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

def test_download_functionality():
    """Test file download functionality"""
    print("\nTesting download functionality...")
    
    # Test login as admin
    admin_data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(
            'https://127.0.0.1:5000/api/auth/login',
            json=admin_data,
            verify=False
        )
        
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print("✓ Admin login successful")
            
            # Get files
            headers = {'Authorization': f'Bearer {admin_token}'}
            response = requests.get(
                'https://127.0.0.1:5000/api/user/files',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                owned_files = data.get('owned_files', [])
                shared_files = data.get('shared_files', [])
                
                print(f"✓ Found {len(owned_files)} owned files and {len(shared_files)} shared files")
                
                # Test download with first available file
                test_file = None
                if owned_files:
                    test_file = owned_files[0]
                    print(f"  - Testing with owned file: {test_file.get('filename')}")
                elif shared_files:
                    test_file = shared_files[0]
                    print(f"  - Testing with shared file: {test_file.get('filename')}")
                else:
                    print("  - No files available for testing")
                    return
                
                if test_file:
                    file_id = test_file.get('id')
                    filename = test_file.get('filename')
                    
                    # Test download
                    response = requests.get(
                        f'https://127.0.0.1:5000/api/user/files/{file_id}/download',
                        headers=headers,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        print(f"✓ Download successful for file: {filename}")
                        print(f"  - Content length: {len(response.content)} bytes")
                        
                        # Test saving to temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                            temp_file.write(response.content)
                            temp_path = temp_file.name
                        
                        if os.path.exists(temp_path):
                            file_size = os.path.getsize(temp_path)
                            print(f"  - File saved successfully: {temp_path}")
                            print(f"  - File size: {file_size} bytes")
                            
                            # Clean up
                            os.unlink(temp_path)
                            print("  - Temporary file cleaned up")
                        else:
                            print("  ✗ Failed to save file")
                    else:
                        print(f"✗ Download failed: {response.status_code}")
                        if response.text:
                            print(f"  - Error: {response.text}")
            else:
                print(f"✗ Failed to get files: {response.status_code}")
        else:
            print(f"✗ Admin login failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error testing download: {e}")

def main():
    """Main test function"""
    print("=== Download Functionality Test ===\n")
    
    # Test backend connection first
    if not test_backend_connection():
        print("\nBackend is not running. Please start the backend server first.")
        print("Run: cd backend && python run.py")
        return
    
    # Test download functionality
    test_download_functionality()
    
    print("\n=== Test completed ===")
    print("\nTo test the GUI download:")
    print("1. Start the main application")
    print("2. Login as any user")
    print("3. Go to Cryptographie section")
    print("4. Click 'Vos fichiers'")
    print("5. Select a file and click 'Télécharger'")

if __name__ == "__main__":
    main() 