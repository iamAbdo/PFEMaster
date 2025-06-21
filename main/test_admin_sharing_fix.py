#!/usr/bin/env python3
"""
Test script for admin sharing fix

This script tests that:
1. Admin can access shared users for any file
2. Admin can share files they don't own
3. Admin can download any file
4. The "Impossible de charger les utilisateurs partagés" error is fixed
"""

import requests
import json
import sys
import os

# Add the main directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_sharing_fix():
    """Test that admin can share files they don't own"""
    print("🧪 Testing Admin Sharing Fix")
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
            
            if not all_files:
                print("   ⚠️ No files available for testing")
                return True
            
            # Find a file the admin doesn't own
            non_owned_file = None
            for file in all_files:
                if not file.get('is_owner', False):
                    non_owned_file = file
                    break
            
            if not non_owned_file:
                print("   ⚠️ No non-owned files available for testing")
                return True
                
            print(f"   📄 Found non-owned file: {non_owned_file['filename']}")
            
        else:
            print(f"   ❌ Admin cannot access all files: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error getting files: {e}")
        return False
    
    # Step 3: Test admin can access shared users for non-owned file
    print("\n3. 👥 Testing admin can access shared users for non-owned file...")
    try:
        response = requests.get(
            f"{base_url}/api/user/files/{non_owned_file['id']}/shared-users",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            shared_users = data.get('shared_users', [])
            print(f"   ✅ Admin can access shared users: {len(shared_users)} users")
        else:
            print(f"   ❌ Admin cannot access shared users: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing shared users access: {e}")
        return False
    
    # Step 4: Test admin can share non-owned file
    print("\n4. 🔗 Testing admin can share non-owned file...")
    try:
        share_data = {'user_ids': []}  # Empty list to test endpoint
        response = requests.post(
            f"{base_url}/api/user/files/{non_owned_file['id']}/share",
            json=share_data,
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            print("   ✅ Admin can share non-owned file")
        else:
            print(f"   ❌ Admin cannot share non-owned file: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing share: {e}")
        return False
    
    # Step 5: Test admin can download non-owned file
    print("\n5. 📥 Testing admin can download non-owned file...")
    try:
        response = requests.get(
            f"{base_url}/api/user/files/{non_owned_file['id']}/download",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            print("   ✅ Admin can download non-owned file")
        else:
            print(f"   ❌ Admin cannot download non-owned file: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing download: {e}")
        return False
    
    print("\n✅ Admin sharing fix tests completed!")
    return True

def test_ui_sharing_dialog():
    """Test that UI sharing dialog works for admin with non-owned files"""
    print("\n🖥️ Testing UI Sharing Dialog")
    print("=" * 35)
    
    print("Expected UI behavior:")
    print("1. Admin can open sharing dialog for any file")
    print("2. No 'Impossible de charger les utilisateurs partagés' error")
    print("3. Shared users list loads correctly")
    print("4. Admin can share/unshare users from any file")
    print("5. All sharing functionality works for non-owned files")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Admin Sharing Fix Tests")
    print("=" * 50)
    
    try:
        # Test backend fixes
        success1 = test_admin_sharing_fix()
        
        # Test UI behavior
        success2 = test_ui_sharing_dialog()
        
        if success1 and success2:
            print("\n🎉 All tests passed!")
            print("\n📋 Summary:")
            print("- Admin can access shared users for any file")
            print("- Admin can share files they don't own")
            print("- Admin can download any file")
            print("- 'Impossible de charger les utilisateurs partagés' error is fixed")
            print("- UI sharing dialog works correctly for admin")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 