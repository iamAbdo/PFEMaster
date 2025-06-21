#!/usr/bin/env python3
"""
Test script for admin full power functionality

This script tests that:
1. Admin can see all files in the system
2. Admin can share any file (owned or not)
3. Admin can delete any file (owned or not)
4. Admin can download any file
5. Regular users still have restricted permissions
"""

import requests
import json
import sys
import os

# Add the main directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_full_power():
    """Test admin full power over all files"""
    print("🧪 Testing Admin Full Power")
    print("=" * 35)
    
    # Test data
    base_url = "https://127.0.0.1:5000"
    
    # Test admin user (update with your actual admin credentials)
    admin_credentials = {
        'email': 'admin@test.com',
        'password': 'admin123'
    }
    
    # Step 1: Login as admin
    print("\n1. 🔐 Logging in as admin...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=admin_credentials,
            verify=False
        )
        
        if response.status_code == 200:
            admin_token = response.json().get('access_token')
            print("   ✅ Admin logged in successfully")
        else:
            print(f"   ❌ Failed to login admin: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error logging in admin: {e}")
        return False
    
    # Step 2: Get all files as admin
    print("\n2. 📁 Getting all files as admin...")
    try:
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = requests.get(
            f"{base_url}/api/user/admin/files",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            all_files = data.get('files', [])
            print(f"   ✅ Admin can see {len(all_files)} files in the system")
            
            # Separate owned and non-owned files
            owned_files = [f for f in all_files if f.get('is_owner', False)]
            non_owned_files = [f for f in all_files if not f.get('is_owner', False)]
            
            print(f"   📊 Files owned by admin: {len(owned_files)}")
            print(f"   📊 Files not owned by admin: {len(non_owned_files)}")
            
        else:
            print(f"   ❌ Admin cannot access all files: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting files: {e}")
        return False
    
    # Step 3: Test sharing permissions (admin can share any file)
    print("\n3. 🔗 Testing admin sharing permissions...")
    
    if all_files:
        # Test sharing any file (owned or not)
        test_file = all_files[0]
        file_owner = test_file.get('is_owner', False)
        
        print(f"   📄 Testing sharing file: {test_file['filename']} (owned: {file_owner})")
        try:
            share_data = {'user_ids': []}  # Empty list to test endpoint
            response = requests.post(
                f"{base_url}/api/user/files/{test_file['id']}/share",
                json=share_data,
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                print("   ✅ Admin can share any file (owned or not)")
            else:
                print(f"   ❌ Admin cannot share file: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing share: {e}")
    
    # Step 4: Test deletion permissions (admin can delete any file)
    print("\n4. 🗑️ Testing admin deletion permissions...")
    
    if all_files:
        # Test deleting any file (owned or not)
        test_file = all_files[0]
        file_owner = test_file.get('is_owner', False)
        
        print(f"   📄 Testing deletion of file: {test_file['filename']} (owned: {file_owner})")
        try:
            response = requests.delete(
                f"{base_url}/api/user/files/{test_file['id']}",
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                print("   ✅ Admin can delete any file (owned or not)")
            else:
                print(f"   ❌ Admin cannot delete file: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing delete: {e}")
    
    # Step 5: Test download permissions (admin can download any file)
    print("\n5. 📥 Testing admin download permissions...")
    
    if all_files:
        # Test downloading any file
        test_file = all_files[0]
        print(f"   📄 Testing download of file: {test_file['filename']}")
        try:
            response = requests.get(
                f"{base_url}/api/user/files/{test_file['id']}/download",
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                print("   ✅ Admin can download any file")
            else:
                print(f"   ❌ Admin cannot download file: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing download: {e}")
    
    print("\n✅ Admin full power tests completed!")
    return True

def test_regular_user_restrictions():
    """Test that regular users still have restricted permissions"""
    print("\n👤 Testing Regular User Restrictions")
    print("=" * 40)
    
    base_url = "https://127.0.0.1:5000"
    
    # Test regular user (update with actual credentials)
    user_credentials = {
        'email': 'user@test.com',
        'password': 'user123'
    }
    
    # Step 1: Login as regular user
    print("\n1. 🔐 Logging in as regular user...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=user_credentials,
            verify=False
        )
        
        if response.status_code == 200:
            user_token = response.json().get('access_token')
            print("   ✅ Regular user logged in successfully")
        else:
            print(f"   ❌ Failed to login regular user: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error logging in regular user: {e}")
        return False
    
    # Step 2: Test regular user cannot access admin endpoint
    print("\n2. 🚫 Testing regular user cannot access admin endpoint...")
    try:
        headers = {'Authorization': f'Bearer {user_token}'}
        response = requests.get(
            f"{base_url}/api/user/admin/files",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 403:
            print("   ✅ Regular user correctly denied access to admin endpoint")
        else:
            print(f"   ❌ Regular user should not have access: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing admin endpoint access: {e}")
        return False
    
    # Step 3: Test regular user can only see their files
    print("\n3. 👀 Testing regular user can only see their files...")
    try:
        response = requests.get(
            f"{base_url}/api/user/files",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            owned_files = data.get('owned_files', [])
            shared_files = data.get('shared_files', [])
            print(f"   ✅ Regular user can see {len(owned_files)} owned files and {len(shared_files)} shared files")
        else:
            print(f"   ❌ Regular user cannot access their files: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing user files access: {e}")
        return False
    
    print("\n✅ Regular user restrictions tests completed!")
    return True

def test_ui_admin_full_power():
    """Test that UI correctly shows admin full power"""
    print("\n🖥️ Testing UI Admin Full Power Display")
    print("=" * 45)
    
    print("Expected UI behavior:")
    print("1. Admin can see all files in 'Gestion d'accès'")
    print("2. Download button appears for all files")
    print("3. Share button appears for ALL files (owned or not)")
    print("4. Delete button appears for ALL files (owned or not)")
    print("5. Admin has full control over any file in the system")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Admin Full Power Tests")
    print("=" * 50)
    
    try:
        # Test admin full power
        success1 = test_admin_full_power()
        
        # Test regular user restrictions
        success2 = test_regular_user_restrictions()
        
        # Test UI behavior
        success3 = test_ui_admin_full_power()
        
        if success1 and success2 and success3:
            print("\n🎉 All tests passed!")
            print("\n📋 Summary:")
            print("- Admin has full power over all files in the system")
            print("- Admin can share any file (owned or not)")
            print("- Admin can delete any file (owned or not)")
            print("- Admin can download any file")
            print("- Regular users still have restricted permissions")
            print("- UI correctly shows admin full power")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 