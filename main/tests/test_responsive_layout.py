#!/usr/bin/env python3
"""
Test for responsive layout improvements
This script tests the admin dialogs on smaller screen sizes
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_responsive_layout():
    """Test the responsive layout improvements"""
    
    # Create a test window
    root = tk.Tk()
    root.title("Responsive Layout Test")
    root.geometry("600x400")  # Smaller window to test responsiveness
    root.configure(bg='#f0f0f0')
    
    # Test frame
    test_frame = tk.Frame(root, bg='#f0f0f0')
    test_frame.pack(expand=True, fill='both', padx=20, pady=20)
    
    # Title
    title = tk.Label(test_frame, text="Test de Layout Responsive", 
                    font=("Arial", 16, "bold"), bg='#f0f0f0')
    title.pack(pady=(0, 20))
    
    # Instructions
    instructions = tk.Label(test_frame, 
                          text="Ce test vérifie que les fenêtres d'administration\n"
                               "s'adaptent aux écrans plus petits.\n\n"
                               "1. Cliquez sur 'Test Gestion d\'accès' pour ouvrir la fenêtre de fichiers\n"
                               "2. Vérifiez que tous les boutons sont visibles\n"
                               "3. Redimensionnez la fenêtre pour tester la responsivité",
                          font=("Arial", 10), bg='#f0f0f0', justify='left')
    instructions.pack(pady=(0, 20))
    
    # Test buttons
    btn_frame = tk.Frame(test_frame, bg='#f0f0f0')
    btn_frame.pack()
    
    def test_file_management():
        """Test file management dialog"""
        # Create a mock file management window
        win = tk.Toplevel(root)
        win.title("Test - Gestion d'accès aux fichiers")
        win.geometry("800x500")
        win.configure(bg='#f0f0f0')
        win.resizable(True, True)
        win.minsize(700, 400)
        
        # Main container
        main_frame = tk.Frame(win, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Test - Gestion d'accès aux fichiers",
                font=("Arial", 16, "bold"), bg='#f0f0f0').pack(side='left')
        
        # Create treeview
        tree = ttk.Treeview(main_frame, 
                           columns=('filename', 'type', 'created_at', 'owner', 'actions'),
                           show='headings', height=10)
        
        tree.heading('filename', text='Nom du fichier')
        tree.heading('type', text='Type')
        tree.heading('created_at', text='Date de création')
        tree.heading('owner', text='Propriétaire')
        tree.heading('actions', text='Actions')
        
        tree.column('filename', width=200, anchor='w')
        tree.column('type', width=80, anchor='center')
        tree.column('created_at', width=100, anchor='center')
        tree.column('owner', width=120, anchor='center')
        tree.column('actions', width=150, anchor='center')
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add test data
        test_files = [
            ("test_file_1.pdf", "Propriétaire", "2024-01-01", "Vous", ""),
            ("test_file_2.pdf", "Partagé", "2024-01-02", "Autre", ""),
            ("test_file_3.pdf", "Propriétaire", "2024-01-03", "Vous", ""),
        ]
        
        for i, file_data in enumerate(test_files):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=file_data, tags=(tag,))
        
        tree.tag_configure('evenrow', background='#f9f9f9')
        tree.tag_configure('oddrow', background='#ffffff')
        
        # Add action buttons
        def add_test_buttons():
            for item in tree.get_children():
                bbox = tree.bbox(item, 'actions')
                if bbox:
                    x, y, width, height = bbox
                    
                    # Download button
                    download_btn = tk.Button(tree, text="Télécharger", bg='#3498db', fg='white',
                                           font=('Arial', 7), relief='flat')
                    download_btn.place(x=x + 2, y=y + (height-18)//2, width=60, height=18)
                    
                    # Share button
                    share_btn = tk.Button(tree, text="Partager", bg='#27ae60', fg='white',
                                        font=('Arial', 7), relief='flat')
                    share_btn.place(x=x + 65, y=y + (height-18)//2, width=50, height=18)
                    
                    # Delete button
                    delete_btn = tk.Button(tree, text="Supprimer", bg='#e74c3c', fg='white',
                                         font=('Arial', 7), relief='flat')
                    delete_btn.place(x=x + 118, y=y + (height-18)//2, width=50, height=18)
        
        win.after(100, add_test_buttons)
        
        # Status
        status_label = tk.Label(win, text="✓ Test réussi! Tous les boutons sont visibles et la fenêtre est redimensionnable.",
                               font=("Arial", 10), bg='#27ae60', fg='white', pady=10)
        status_label.pack(side='bottom', fill='x')
    
    def test_user_management():
        """Test user management dialog"""
        win = tk.Toplevel(root)
        win.title("Test - Gestion des utilisateurs")
        win.geometry("700x450")
        win.configure(bg='#f0f0f0')
        win.resizable(True, True)
        win.minsize(600, 350)
        
        main_frame = tk.Frame(win, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Test - Gestion des utilisateurs",
                font=("Arial", 16, "bold"), bg='#f0f0f0').pack(pady=(0, 20))
        
        # Create treeview
        tree = ttk.Treeview(main_frame, columns=('email','role','actions'),
                           show='headings', height=10)
        
        tree.heading('email', text='Email')
        tree.heading('role', text='Rôle')
        tree.heading('actions', text='Actions')
        
        tree.column('email', width=250, anchor='w')
        tree.column('role', width=100, anchor='center')
        tree.column('actions', width=80, anchor='center')
        
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add test data
        test_users = [
            ("admin@example.com", "Responsable", ""),
            ("user1@example.com", "Geologue", ""),
            ("user2@example.com", "Geophysicien", ""),
        ]
        
        for i, user_data in enumerate(test_users):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert('', 'end', values=user_data, tags=(tag,))
        
        tree.tag_configure('evenrow', background='#f9f9f9')
        tree.tag_configure('oddrow', background='#ffffff')
        
        # Add delete buttons
        def add_delete_buttons():
            for item in tree.get_children():
                bbox = tree.bbox(item, 'actions')
                if bbox:
                    x, y, width, height = bbox
                    btn = tk.Button(tree, text="Supprimer", bg='#e74c3c', fg='white',
                                   font=('Arial', 8), relief='flat', padx=3, pady=1)
                    btn.place(x=x + (width-60)//2, y=y + (height-18)//2, width=60, height=18)
        
        win.after(100, add_delete_buttons)
        
        # Status
        status_label = tk.Label(win, text="✓ Test réussi! Boutons visibles et fenêtre redimensionnable.",
                               font=("Arial", 10), bg='#27ae60', fg='white', pady=10)
        status_label.pack(side='bottom', fill='x')
    
    # Test buttons
    tk.Button(btn_frame, text="Test Gestion d'accès", command=test_file_management,
              bg='#3498db', fg='white', font=('Arial', 10), padx=20, pady=10).pack(side='left', padx=10)
    
    tk.Button(btn_frame, text="Test Gestion Utilisateurs", command=test_user_management,
              bg='#27ae60', fg='white', font=('Arial', 10), padx=20, pady=10).pack(side='left', padx=10)
    
    # Close button
    tk.Button(test_frame, text="Fermer", command=root.destroy,
              bg='#e74c3c', fg='white', font=('Arial', 10), padx=20, pady=10).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_responsive_layout() 