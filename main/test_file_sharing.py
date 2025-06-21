#!/usr/bin/env python3
"""
Test script for file sharing features
This script tests the file sharing functionality for Responsable users
"""

import requests
import json

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

def test_user_roles():
    """Test user role functionality"""
    print("\nTesting user roles...")
    
    # Test login as admin (Responsable)
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
            
            # Test getting geologues
            headers = {'Authorization': f'Bearer {admin_token}'}
            response = requests.get(
                'https://127.0.0.1:5000/api/user/users/geologues',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                geologues = data.get('geologues', [])
                print(f"✓ Found {len(geologues)} Geologue users")
                
                for geologue in geologues:
                    print(f"  - {geologue.get('email')} (ID: {geologue.get('id')})")
                
                return admin_token, geologues
            else:
                print(f"✗ Failed to get geologues: {response.status_code}")
                return None, []
        else:
            print(f"✗ Admin login failed: {response.status_code}")
            return None, []
            
    except Exception as e:
        print(f"✗ Error testing user roles: {e}")
        return None, []

def test_file_sharing(admin_token, geologues):
    """Test file sharing functionality"""
    print("\nTesting file sharing...")
    
    if not admin_token or not geologues:
        print("✗ Cannot test file sharing without admin token or geologues")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Get admin's files
    try:
        response = requests.get(
            'https://127.0.0.1:5000/api/user/files',
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            owned_files = data.get('owned_files', [])
            
            if owned_files:
                test_file = owned_files[0]
                file_id = test_file.get('id')
                filename = test_file.get('filename')
                
                print(f"✓ Using test file: {filename} (ID: {file_id})")
                
                # Test sharing with first geologue
                if geologues:
                    geologue_id = geologues[0].get('id')
                    geologue_email = geologues[0].get('email')
                    
                    share_data = {'user_ids': [geologue_id]}
                    
                    response = requests.post(
                        f'https://127.0.0.1:5000/api/user/files/{file_id}/share',
                        json=share_data,
                        headers=headers,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✓ File shared successfully with {geologue_email}")
                        print(f"  - Shared with: {data.get('shared_with', [])}")
                        print(f"  - Total shared users: {data.get('total_shared_users', 0)}")
                        
                        # Test getting shared users
                        response = requests.get(
                            f'https://127.0.0.1:5000/api/user/files/{file_id}/shared-users',
                            headers=headers,
                            verify=False
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            shared_users = data.get('shared_users', [])
                            print(f"✓ Found {len(shared_users)} shared users")
                            
                            # Test unsharing
                            response = requests.post(
                                f'https://127.0.0.1:5000/api/user/files/{file_id}/unshare',
                                json=share_data,
                                headers=headers,
                                verify=False
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                print(f"✓ File access removed successfully")
                                print(f"  - Removed from: {data.get('removed_from', [])}")
                                print(f"  - Total shared users: {data.get('total_shared_users', 0)}")
                            else:
                                print(f"✗ Failed to unshare file: {response.status_code}")
                        else:
                            print(f"✗ Failed to get shared users: {response.status_code}")
                    else:
                        print(f"✗ Failed to share file: {response.status_code}")
                else:
                    print("✗ No geologues available for testing")
            else:
                print("✗ No owned files available for testing")
        else:
            print(f"✗ Failed to get files: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error testing file sharing: {e}")

def main():
    """Main test function"""
    print("=== File Sharing Features Test ===\n")
    
    # Test backend connection first
    if not test_backend_connection():
        print("\nBackend is not running. Please start the backend server first.")
        print("Run: cd backend && python run.py")
        return
    
    # Test user roles
    admin_token, geologues = test_user_roles()
    
    # Test file sharing
    test_file_sharing(admin_token, geologues)
    
    print("\n=== Test completed ===")
    print("\nTo test the GUI:")
    print("1. Start the main application")
    print("2. Login as a Responsable user")
    print("3. Go to Cryptographie section")
    print("4. Click 'Vos fichiers'")
    print("5. Select a file and click 'Partager'")

if __name__ == "__main__":
    main() 