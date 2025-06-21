#!/usr/bin/env python3
"""
Debug test for file sharing functionality
This script tests the file sharing step by step to identify issues
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

def test_file_sharing_debug():
    """Debug file sharing functionality"""
    print("\n=== File Sharing Debug Test ===")
    
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
            
            headers = {'Authorization': f'Bearer {admin_token}'}
            
            # Step 1: Get geologues
            print("\n1. Testing get geologues...")
            response = requests.get(
                'https://127.0.0.1:5000/api/user/users/geologues',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                geologues = data.get('geologues', [])
                print(f"✓ Found {len(geologues)} geologues")
                for geologue in geologues:
                    print(f"  - {geologue.get('email')} (ID: {geologue.get('id')})")
            else:
                print(f"✗ Failed to get geologues: {response.status_code}")
                print(f"  Response: {response.text}")
                return
            
            # Step 2: Get files
            print("\n2. Testing get files...")
            response = requests.get(
                'https://127.0.0.1:5000/api/user/files',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                owned_files = data.get('owned_files', [])
                print(f"✓ Found {len(owned_files)} owned files")
                
                if not owned_files:
                    print("✗ No owned files available for testing")
                    return
                
                test_file = owned_files[0]
                file_id = test_file.get('id')
                filename = test_file.get('filename')
                print(f"  - Using file: {filename} (ID: {file_id})")
            else:
                print(f"✗ Failed to get files: {response.status_code}")
                print(f"  Response: {response.text}")
                return
            
            # Step 3: Get current shared users
            print("\n3. Testing get shared users...")
            response = requests.get(
                f'https://127.0.0.1:5000/api/user/files/{file_id}/shared-users',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                shared_users = data.get('shared_users', [])
                print(f"✓ Found {len(shared_users)} current shared users")
                for user in shared_users:
                    print(f"  - {user.get('email')} (ID: {user.get('id')})")
            else:
                print(f"✗ Failed to get shared users: {response.status_code}")
                print(f"  Response: {response.text}")
                return
            
            # Step 4: Test sharing with first geologue
            if geologues:
                geologue_id = geologues[0].get('id')
                geologue_email = geologues[0].get('email')
                
                print(f"\n4. Testing share file with {geologue_email}...")
                
                share_data = {'user_ids': [geologue_id]}
                print(f"  - Share data: {share_data}")
                
                response = requests.post(
                    f'https://127.0.0.1:5000/api/user/files/{file_id}/share',
                    json=share_data,
                    headers=headers,
                    verify=False
                )
                
                print(f"  - Response status: {response.status_code}")
                print(f"  - Response: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Share successful!")
                    print(f"  - Shared with: {data.get('shared_with', [])}")
                    print(f"  - Total shared users: {data.get('total_shared_users', 0)}")
                    
                    # Step 5: Verify shared users after sharing
                    print("\n5. Verifying shared users after sharing...")
                    response = requests.get(
                        f'https://127.0.0.1:5000/api/user/files/{file_id}/shared-users',
                        headers=headers,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        shared_users = data.get('shared_users', [])
                        print(f"✓ Now have {len(shared_users)} shared users")
                        for user in shared_users:
                            print(f"  - {user.get('email')} (ID: {user.get('id')})")
                    else:
                        print(f"✗ Failed to verify shared users: {response.status_code}")
                        
                else:
                    print(f"✗ Share failed: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"  - Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        print(f"  - Error: {response.text}")
            else:
                print("✗ No geologues available for testing")
                
        else:
            print(f"✗ Admin login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")

def main():
    """Main test function"""
    print("=== File Sharing Debug Test ===\n")
    
    # Test backend connection first
    if not test_backend_connection():
        print("\nBackend is not running. Please start the backend server first.")
        print("Run: cd backend && python run.py")
        return
    
    # Test file sharing debug
    test_file_sharing_debug()
    
    print("\n=== Debug Test completed ===")

if __name__ == "__main__":
    main() 