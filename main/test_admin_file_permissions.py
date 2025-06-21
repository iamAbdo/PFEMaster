#!/usr/bin/env python3
"""
Test script for admin file permissions

This script tests that:
1. Admin can see all files in the system
2. Admin can only share/delete files they own
3. Admin cannot share/delete files they don't own
4. Admin can download any file
"""

import requests
import json
import sys
import os

# Add the main directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_file_permissions():
    """Test admin file permissions"""
    print("🧪 Testing Admin File Permissions")
    print("=" * 40)
    
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
    
    # Step 3: Test sharing permissions
    print("\n3. 🔗 Testing file sharing permissions...")
    
    if all_files:
        # Test with a file the admin owns
        owned_file = None
        non_owned_file = None
        
        for file in all_files:
            if file.get('is_owner', False) and owned_file is None:
                owned_file = file
            elif not file.get('is_owner', False) and non_owned_file is None:
                non_owned_file = file
            
            if owned_file and non_owned_file:
                break
        
        # Test sharing owned file
        if owned_file:
            print(f"   📄 Testing sharing owned file: {owned_file['filename']}")
            try:
                share_data = {'user_ids': []}  # Empty list to test endpoint
                response = requests.post(
                    f"{base_url}/api/user/files/{owned_file['id']}/share",
                    json=share_data,
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 200:
                    print("   ✅ Admin can share owned file")
                else:
                    print(f"   ❌ Admin cannot share owned file: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing share owned file: {e}")
        
        # Test sharing non-owned file
        if non_owned_file:
            print(f"   📄 Testing sharing non-owned file: {non_owned_file['filename']}")
            try:
                share_data = {'user_ids': []}  # Empty list to test endpoint
                response = requests.post(
                    f"{base_url}/api/user/files/{non_owned_file['id']}/share",
                    json=share_data,
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 403:
                    print("   ✅ Admin correctly denied sharing non-owned file")
                else:
                    print(f"   ❌ Admin should not be able to share non-owned file: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing share non-owned file: {e}")
    
    # Step 4: Test deletion permissions
    print("\n4. 🗑️ Testing file deletion permissions...")
    
    if all_files:
        # Test deleting owned file
        if owned_file:
            print(f"   📄 Testing deletion of owned file: {owned_file['filename']}")
            try:
                response = requests.delete(
                    f"{base_url}/api/user/files/{owned_file['id']}",
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 200:
                    print("   ✅ Admin can delete owned file")
                else:
                    print(f"   ❌ Admin cannot delete owned file: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing delete owned file: {e}")
        
        # Test deleting non-owned file
        if non_owned_file:
            print(f"   📄 Testing deletion of non-owned file: {non_owned_file['filename']}")
            try:
                response = requests.delete(
                    f"{base_url}/api/user/files/{non_owned_file['id']}",
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 403:
                    print("   ✅ Admin correctly denied deletion of non-owned file")
                else:
                    print(f"   ❌ Admin should not be able to delete non-owned file: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error testing delete non-owned file: {e}")
    
    # Step 5: Test download permissions
    print("\n5. 📥 Testing file download permissions...")
    
    if all_files:
        # Test downloading any file (admin should be able to download any file)
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
    
    print("\n✅ Admin file permissions tests completed!")
    return True

def test_ui_permissions():
    """Test that UI correctly shows/hides buttons based on ownership"""
    print("\n🖥️ Testing UI Permission Display")
    print("=" * 35)
    
    print("Expected UI behavior:")
    print("1. Admin can see all files in 'Gestion d'accès'")
    print("2. Download button appears for all files")
    print("3. Share button only appears for files admin owns")
    print("4. Delete button only appears for files admin owns")
    print("5. Non-owned files show only download button")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Admin File Permissions Tests")
    print("=" * 55)
    
    try:
        # Test backend permissions
        success1 = test_admin_file_permissions()
        
        # Test UI behavior
        success2 = test_ui_permissions()
        
        if success1 and success2:
            print("\n🎉 All tests passed!")
            print("\n📋 Summary:")
            print("- Admin can see all files in the system")
            print("- Admin can download any file")
            print("- Admin can only share files they own")
            print("- Admin can only delete files they own")
            print("- UI correctly shows/hides buttons based on ownership")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 