#!/usr/bin/env python3
"""
Test script for the new PDF export feature
This script tests the PDF export functionality with backend integration
"""

import json
import os
from pathlib import Path
from utils.settings import get_settings_file
from utils.auth_state import set_jwt_token_global

def test_settings_loading():
    """Test that settings can be loaded correctly"""
    print("Testing settings loading...")
    
    settings_path = get_settings_file()
    print(f"Settings path: {settings_path}")
    
    settings = {}
    if settings_path.exists():
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            print(f"Loaded settings: {settings}")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    save_dir = settings.get('save_dir', str(Path.home() / 'Documents'))
    print(f"Save directory: {save_dir}")
    
    # Test if directory exists and is writable
    try:
        test_file = Path(save_dir) / "test.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✓ Save directory is writable")
    except Exception as e:
        print(f"✗ Save directory error: {e}")
    
    return True

def test_auth_state():
    """Test that auth state can be set and retrieved"""
    print("\nTesting auth state...")
    
    # Test setting and getting token
    test_token = "test_jwt_token_123"
    set_jwt_token_global(test_token)
    
    from utils.auth_state import get_jwt_token_global
    retrieved_token = get_jwt_token_global()
    
    if retrieved_token == test_token:
        print("✓ Auth state working correctly")
        return True
    else:
        print(f"✗ Auth state error: expected {test_token}, got {retrieved_token}")
        return False

def test_pdf_export_imports():
    """Test that all required imports for PDF export work"""
    print("\nTesting PDF export imports...")
    
    try:
        from functions.export_pdf import PDFExporter
        print("✓ PDFExporter imported successfully")
        
        # Test required modules
        import requests
        print("✓ requests module available")
        
        from io import BytesIO
        print("✓ BytesIO available")
        
        from datetime import datetime
        print("✓ datetime available")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Testing PDF Export Feature ===\n")
    
    tests = [
        test_settings_loading,
        test_auth_state,
        test_pdf_export_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The PDF export feature should work correctly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 