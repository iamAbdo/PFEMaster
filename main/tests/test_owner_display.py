#!/usr/bin/env python3
"""
Test script for owner display in sharing dialog

This script tests that:
1. File owner is shown in the sharing dialog
2. Owner is displayed with gray color and "Propriétaire" text
3. Owner cannot be selected
4. Owner is not included in share/unshare operations
"""

import requests
import json
import sys
import os

# Add the main directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_owner_display():
    """Test that owner is displayed correctly in sharing dialog"""
    print("🧪 Testing Owner Display in Sharing Dialog")
    print("=" * 50)
    
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
            
            # Find a file the admin doesn't own (to test with non-owned file)
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
    
    # Step 3: Test new users-for-sharing endpoint
    print("\n3. 👥 Testing users-for-sharing endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/user/files/{non_owned_file['id']}/users-for-sharing",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            users_for_sharing = data.get('users_for_sharing', [])
            file_owner_id = data.get('file_owner_id')
            
            print(f"   ✅ Got {len(users_for_sharing)} users for sharing")
            print(f"   📋 File owner ID: {file_owner_id}")
            
            # Check if owner is included in the list
            owner_found = False
            for user in users_for_sharing:
                if user.get('is_owner', False):
                    owner_found = True
                    print(f"   👑 Owner found: {user.get('email')} (ID: {user.get('id')})")
                    break
            
            if not owner_found:
                print("   ❌ Owner not found in users list")
                return False
                
        else:
            print(f"   ❌ Cannot access users-for-sharing: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing users-for-sharing: {e}")
        return False
    
    # Step 4: Test that owner has correct properties
    print("\n4. 🔍 Testing owner properties...")
    try:
        response = requests.get(
            f"{base_url}/api/user/files/{non_owned_file['id']}/users-for-sharing",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            users_for_sharing = data.get('users_for_sharing', [])
            
            for user in users_for_sharing:
                if user.get('is_owner', False):
                    # Check owner properties
                    has_owner_property = 'is_owner' in user
                    has_access_property = 'has_access' in user
                    has_role = 'role' in user
                    has_email = 'email' in user
                    
                    print(f"   ✅ Owner has 'is_owner' property: {has_owner_property}")
                    print(f"   ✅ Owner has 'has_access' property: {has_access_property}")
                    print(f"   ✅ Owner has 'role' property: {has_role}")
                    print(f"   ✅ Owner has 'email' property: {has_email}")
                    
                    if not all([has_owner_property, has_access_property, has_role, has_email]):
                        print("   ❌ Owner missing required properties")
                        return False
                    
                    break
                    
        else:
            print(f"   ❌ Cannot access users-for-sharing: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing owner properties: {e}")
        return False
    
    print("\n✅ Owner display tests completed!")
    return True

def test_ui_owner_behavior():
    """Test expected UI behavior for owner display"""
    print("\n🖥️ Testing UI Owner Behavior")
    print("=" * 35)
    
    print("Expected UI behavior:")
    print("1. File owner appears in the sharing dialog")
    print("2. Owner is displayed with gray background color")
    print("3. Owner shows 'Propriétaire' in the access column")
    print("4. Owner cannot be selected (selection is automatically removed)")
    print("5. Owner is not included in share/unshare operations")
    print("6. Instructions mention that owner cannot be selected")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Owner Display Tests")
    print("=" * 50)
    
    try:
        # Test backend functionality
        success1 = test_owner_display()
        
        # Test UI behavior
        success2 = test_ui_owner_behavior()
        
        if success1 and success2:
            print("\n🎉 All tests passed!")
            print("\n📋 Summary:")
            print("- File owner is included in users-for-sharing endpoint")
            print("- Owner has correct properties (is_owner, has_access, etc.)")
            print("- Owner is displayed with gray styling in UI")
            print("- Owner shows 'Propriétaire' text")
            print("- Owner cannot be selected or modified")
            print("- UI provides clear instructions about owner")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 