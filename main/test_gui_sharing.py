#!/usr/bin/env python3
"""
Simple GUI test for file sharing dialog
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.file_sharing_dialog import show_file_sharing_dialog
from utils.auth_state import set_jwt_token_global

def test_file_sharing_dialog():
    """Test the file sharing dialog"""
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Test File Sharing")
    root.geometry("400x200")
    
    # Set up test data
    test_file_info = {
        'id': 1,
        'filename': 'test_file.pdf',
        'created_at': '2024-01-01T10:00:00'
    }
    
    # Set a test JWT token (you'll need to replace this with a real token)
    set_jwt_token_global("your_jwt_token_here")
    
    def open_sharing_dialog():
        """Open the file sharing dialog"""
        result = show_file_sharing_dialog(root, test_file_info)
        print(f"Dialog result: {result}")
    
    # Create a button to open the dialog
    btn = tk.Button(root, text="Test File Sharing Dialog", command=open_sharing_dialog)
    btn.pack(pady=50)
    
    # Instructions
    label = tk.Label(root, text="Click the button to test the file sharing dialog.\nMake sure the backend is running first.")
    label.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_file_sharing_dialog() 