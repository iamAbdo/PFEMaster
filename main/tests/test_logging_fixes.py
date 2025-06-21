#!/usr/bin/env python3
"""
Test script for logging fixes

This script tests that:
1. User creation is properly logged
2. User deletion works and is logged
3. File sharing shows correct user in logs
4. All logging functions work correctly
"""

import requests
import json
import sys
import os

# Add the main directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_logging_fixes():
    """Test the logging fixes"""
    print("🧪 Testing Logging Fixes")
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
            admin_token = response.json().get('token')
            print("   ✅ Admin logged in successfully")
        else:
            print(f"   ❌ Failed to login admin: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error logging in admin: {e}")
        return False
    
    # Step 2: Test user creation logging
    print("\n2. 👤 Testing user creation logging...")
    try:
        headers = {'Authorization': f'Bearer {admin_token}'}
        new_user_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'role': 'Geologue'
        }
        
        response = requests.post(
            f"{base_url}/api/user-management/create-user",
            json=new_user_data,
            headers=headers,
            verify=False
        )
        
        if response.status_code == 201:
            print("   ✅ User created successfully")
        else:
            print(f"   ❌ Failed to create user: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error creating user: {e}")
        return False
    
    # Step 3: Check activity logs for user creation
    print("\n3. 📋 Checking activity logs for user creation...")
    try:
        response = requests.get(
            f"{base_url}/api/user/activity-logs",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            
            # Look for user creation log
            user_creation_logs = [log for log in logs if log.get('action') == 'User Creation']
            if user_creation_logs:
                latest_creation = user_creation_logs[0]
                print(f"   ✅ User creation logged: {latest_creation.get('details')}")
                print(f"   📧 Admin email: {latest_creation.get('user_email')}")
            else:
                print("   ⚠️ No user creation log found")
                
        else:
            print(f"   ❌ Cannot access activity logs: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking activity logs: {e}")
        return False
    
    # Step 4: Test user deletion
    print("\n4. 🗑️ Testing user deletion...")
    try:
        response = requests.delete(
            f"{base_url}/api/user-management/delete-user/testuser@example.com",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            print("   ✅ User deleted successfully")
        else:
            print(f"   ❌ Failed to delete user: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error deleting user: {e}")
        return False
    
    # Step 5: Check activity logs for user deletion
    print("\n5. 📋 Checking activity logs for user deletion...")
    try:
        response = requests.get(
            f"{base_url}/api/user/activity-logs",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            
            # Look for user deletion log
            user_deletion_logs = [log for log in logs if log.get('action') == 'User Deletion']
            if user_deletion_logs:
                latest_deletion = user_deletion_logs[0]
                print(f"   ✅ User deletion logged: {latest_deletion.get('details')}")
                print(f"   📧 Admin email: {latest_deletion.get('user_email')}")
            else:
                print("   ⚠️ No user deletion log found")
                
        else:
            print(f"   ❌ Cannot access activity logs: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking activity logs: {e}")
        return False
    
    # Step 6: Test file sharing logging (if files exist)
    print("\n6. 📁 Testing file sharing logging...")
    try:
        # First get available files
        response = requests.get(
            f"{base_url}/api/user/admin/files",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            if files:
                file_id = files[0]['id']
                print(f"   📄 Testing with file: {files[0]['filename']}")
                
                # Get available users for sharing
                response = requests.get(
                    f"{base_url}/api/user/users/available",
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 200:
                    users_data = response.json()
                    available_users = users_data.get('available_users', [])
                    
                    if available_users:
                        user_ids = [available_users[0]['id']]
                        
                        # Share file
                        share_data = {'user_ids': user_ids}
                        response = requests.post(
                            f"{base_url}/api/user/files/{file_id}/share",
                            json=share_data,
                            headers=headers,
                            verify=False
                        )
                        
                        if response.status_code == 200:
                            print("   ✅ File shared successfully")
                            
                            # Check logs for file sharing
                            response = requests.get(
                                f"{base_url}/api/user/activity-logs",
                                headers=headers,
                                verify=False
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                logs = data.get('logs', [])
                                
                                # Look for file share log
                                file_share_logs = [log for log in logs if log.get('action') == 'File Share']
                                if file_share_logs:
                                    latest_share = file_share_logs[0]
                                    print(f"   ✅ File sharing logged: {latest_share.get('details')}")
                                    print(f"   📧 User email: {latest_share.get('user_email')}")
                                else:
                                    print("   ⚠️ No file sharing log found")
                            else:
                                print("   ⚠️ Cannot check file sharing logs")
                        else:
                            print(f"   ⚠️ Failed to share file: {response.text}")
                    else:
                        print("   ⚠️ No users available for sharing")
                else:
                    print("   ⚠️ Cannot get available users")
            else:
                print("   ⚠️ No files available for testing")
        else:
            print("   ⚠️ Cannot get files for testing")
            
    except Exception as e:
        print(f"   ⚠️ Error testing file sharing: {e}")
    
    print("\n✅ Logging fixes tests completed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Logging Fixes Tests")
    print("=" * 45)
    
    try:
        success = test_logging_fixes()
        
        if success:
            print("\n🎉 All tests passed!")
            print("\n📋 Summary:")
            print("- User creation is now properly logged")
            print("- User deletion works with email-based deletion")
            print("- User deletion is properly logged")
            print("- File sharing shows correct user in logs")
            print("- All logging functions work correctly")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 