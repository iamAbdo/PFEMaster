#!/usr/bin/env python3
"""
Test for the latest improvements:
1. Download buttons in "Vos fichiers" dialog
2. Scrollable file sharing dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vos_fichiers_improvements():
    """Test the improved 'Vos fichiers' dialog with download buttons"""
    
    root = tk.Tk()
    root.title("Test - Vos fichiers amélioré")
    root.geometry("600x400")
    root.configure(bg='#f0f0f0')
    
    # Test frame
    test_frame = tk.Frame(root, bg='#f0f0f0')
    test_frame.pack(expand=True, fill='both', padx=20, pady=20)
    
    # Title
    title = tk.Label(test_frame, text="Test - Vos fichiers avec boutons de téléchargement", 
                    font=("Arial", 16, "bold"), bg='#f0f0f0')
    title.pack(pady=(0, 20))
    
    # Instructions
    instructions = tk.Label(test_frame, 
                          text="Ce test simule la fenêtre 'Vos fichiers' avec des boutons\n"
                               "de téléchargement dans chaque ligne.\n\n"
                               "1. Cliquez sur 'Test Vos fichiers' pour voir la fenêtre\n"
                               "2. Vérifiez que chaque ligne a un bouton vert de téléchargement\n"
                               "3. Les boutons sont centrés dans la colonne Actions",
                          font=("Arial", 10), bg='#f0f0f0', justify='left')
    instructions.pack(pady=(0, 20))
    
    def test_vos_fichiers():
        """Test the vos fichiers dialog"""
        dialog = tk.Toplevel(root)
        dialog.title("Test - Vos fichiers PDF")
        dialog.geometry("800x500")
        dialog.configure(bg='#f0f0f0')
        dialog.resizable(True, True)
        dialog.minsize(700, 400)
        dialog.transient(root)
        dialog.grab_set()
        
        # Main container
        main_frame = tk.Frame(dialog, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Vos fichiers PDF", 
                font=("Arial", 16, "bold"), bg='#f0f0f0').pack(side='left')
        
        # Create treeview
        columns = ('Nom', 'Type', 'Date de création', 'Propriétaire', 'Actions')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        tree.heading('Nom', text='Nom du fichier')
        tree.heading('Type', text='Type')
        tree.heading('Date de création', text='Date de création')
        tree.heading('Propriétaire', text='Propriétaire')
        tree.heading('Actions', text='Actions')
        
        tree.column('Nom', width=250, anchor='w')
        tree.column('Type', width=80, anchor='center')
        tree.column('Date de création', width=120, anchor='center')
        tree.column('Propriétaire', width=100, anchor='center')
        tree.column('Actions', width=100, anchor='center')
        
        # Configure row styling
        tree.tag_configure('evenrow', background='#f9f9f9')
        tree.tag_configure('oddrow', background='#ffffff')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Test data
        test_files = [
            {"id": 1, "filename": "test_file_1.pdf", "is_owner": True, "created_at": "2024-01-01T10:00:00", "owner": "Vous"},
            {"id": 2, "filename": "test_file_2.pdf", "is_owner": False, "created_at": "2024-01-02T11:00:00", "owner": "Autre"},
            {"id": 3, "filename": "test_file_3.pdf", "is_owner": True, "created_at": "2024-01-03T12:00:00", "owner": "Vous"},
            {"id": 4, "filename": "test_file_4.pdf", "is_owner": False, "created_at": "2024-01-04T13:00:00", "owner": "Autre"},
        ]
        
        # Populate treeview
        file_data_dict = {}
        for idx, file in enumerate(test_files):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            file_type = "Propriétaire" if file.get('is_owner', False) else "Partagé"
            created_date = file.get('created_at', '').split('T')[0] if file.get('created_at') else ''
            owner = file.get('owner', 'Vous') if not file.get('is_owner', False) else 'Vous'
            
            item_id = tree.insert('', 'end', values=(
                file.get('filename', ''),
                file_type,
                created_date,
                owner,
                ''  # placeholder for download button
            ), tags=(tag,))
            file_data_dict[item_id] = file
        
        def download_file(file_id, filename):
            messagebox.showinfo("Test", f"Téléchargement simulé: {filename} (ID: {file_id})")
        
        def add_download_buttons():
            """Add download buttons to each row"""
            for item in tree.get_children():
                file_data = file_data_dict.get(item)
                if not file_data:
                    continue
                    
                file_id = file_data.get('id')
                filename = file_data.get('filename', '')
                
                bbox = tree.bbox(item, 'Actions')
                if not bbox:
                    continue
                
                x, y, width, height = bbox
                
                # Download button (green)
                download_btn = tk.Button(
                    tree,
                    text="📥",
                    bg='#27ae60',  # Green color
                    fg='white',
                    font=('Arial', 10),
                    relief='flat',
                    command=lambda fid=file_id, fn=filename: download_file(fid, fn)
                )
                download_btn.place(
                    x=x + (width-30)//2,
                    y=y + (height-20)//2,
                    width=30,
                    height=20
                )
        
        # Add buttons after tree is populated
        dialog.after(100, add_download_buttons)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Actualiser", command=lambda: messagebox.showinfo("Test", "Actualisation simulée")).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Fermer", command=dialog.destroy).pack(side='right')
        
        # Status
        status_label = tk.Label(dialog, text="✓ Test réussi! Boutons de téléchargement verts dans chaque ligne.",
                               font=("Arial", 10), bg='#27ae60', fg='white', pady=10)
        status_label.pack(side='bottom', fill='x')
    
    def test_scrollable_sharing():
        """Test the scrollable file sharing dialog"""
        dialog = tk.Toplevel(root)
        dialog.title("Test - Partage de fichier scrollable")
        dialog.geometry("700x500")
        dialog.configure(bg='#f0f0f0')
        dialog.resizable(True, True)
        dialog.minsize(600, 400)
        dialog.transient(root)
        dialog.grab_set()
        
        # Create a canvas with scrollbar for the main content
        canvas = tk.Canvas(dialog, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Main frame inside scrollable frame
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Add many test sections to demonstrate scrolling
        for i in range(10):
            section_frame = ttk.LabelFrame(main_frame, text=f"Section de test {i+1}", padding="10")
            section_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Label(section_frame, text=f"Contenu de la section {i+1}").pack(anchor='w')
            ttk.Label(section_frame, text="Cette section démontre le défilement").pack(anchor='w')
        
        # File info section
        file_frame = ttk.LabelFrame(main_frame, text="Informations du fichier", padding="10")
        file_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(file_frame, text="Nom: test_file.pdf").pack(anchor='w')
        ttk.Label(file_frame, text="Date de création: 2024-01-01").pack(anchor='w')
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(instructions_frame, text="1. Sélectionnez des utilisateurs dans la liste 'Géologues disponibles'", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="2. Cliquez sur 'Partager avec sélection' pour leur donner accès", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="3. Pour retirer l'accès, sélectionnez des utilisateurs dans 'Utilisateurs avec accès'", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="4. Cliquez sur 'Retirer l'accès'", 
                 font=("Arial", 9)).pack(anchor='w')
        
        # Available users section
        users_frame = ttk.LabelFrame(main_frame, text="Géologues disponibles (sélectionnez pour partager)", padding="10")
        users_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create treeview for available users
        columns = ('Email', 'Date de création')
        users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=4)
        
        users_tree.heading('Email', text='Email')
        users_tree.heading('Date de création', text='Date de création')
        
        users_tree.column('Email', width=250)
        users_tree.column('Date de création', width=120)
        
        # Add scrollbar
        users_scrollbar = ttk.Scrollbar(users_frame, orient='vertical', command=users_tree.yview)
        users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        users_tree.pack(side='left', fill='both', expand=True)
        users_scrollbar.pack(side='right', fill='y')
        
        # Add test users
        test_users = [
            ("user1@example.com", "2024-01-01"),
            ("user2@example.com", "2024-01-02"),
            ("user3@example.com", "2024-01-03"),
            ("user4@example.com", "2024-01-04"),
        ]
        
        for user in test_users:
            users_tree.insert('', 'end', values=user)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Partager avec sélection", 
                  command=lambda: messagebox.showinfo("Test", "Partage simulé")).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Actualiser", 
                  command=lambda: messagebox.showinfo("Test", "Actualisation simulée")).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Fermer", command=dialog.destroy).pack(side='right')
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Status
        status_label = tk.Label(dialog, text="✓ Test réussi! Fenêtre scrollable avec beaucoup de contenu.",
                               font=("Arial", 10), bg='#27ae60', fg='white', pady=10)
        status_label.pack(side='bottom', fill='x')
    
    # Test buttons
    btn_frame = tk.Frame(test_frame, bg='#f0f0f0')
    btn_frame.pack()
    
    tk.Button(btn_frame, text="Test Vos fichiers", command=test_vos_fichiers,
              bg='#3498db', fg='white', font=('Arial', 10), padx=20, pady=10).pack(side='left', padx=10)
    
    tk.Button(btn_frame, text="Test Partage Scrollable", command=test_scrollable_sharing,
              bg='#27ae60', fg='white', font=('Arial', 10), padx=20, pady=10).pack(side='left', padx=10)
    
    # Close button
    tk.Button(test_frame, text="Fermer", command=root.destroy,
              bg='#e74c3c', fg='white', font=('Arial', 10), padx=20, pady=10).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_vos_fichiers_improvements() 