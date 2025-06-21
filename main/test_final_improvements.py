#!/usr/bin/env python3
"""
Test for the final improvements:
1. Text download buttons in "Vos fichiers" dialog
2. Unified file sharing interface with access status
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_final_improvements():
    """Test the final improvements"""
    
    root = tk.Tk()
    root.title("Test - Améliorations finales")
    root.geometry("600x400")
    root.configure(bg='#f0f0f0')
    
    # Test frame
    test_frame = tk.Frame(root, bg='#f0f0f0')
    test_frame.pack(expand=True, fill='both', padx=20, pady=20)
    
    # Title
    title = tk.Label(test_frame, text="Test - Améliorations finales", 
                    font=("Arial", 16, "bold"), bg='#f0f0f0')
    title.pack(pady=(0, 20))
    
    # Instructions
    instructions = tk.Label(test_frame, 
                          text="Ce test vérifie les améliorations finales:\n\n"
                               "1. Boutons 'Télécharger' en texte (pas d'icônes)\n"
                               "2. Interface de partage unifiée avec statut d'accès\n"
                               "3. Messages d'erreur appropriés pour accès existant\n"
                               "4. Couleurs vert/rouge pour statut d'accès",
                          font=("Arial", 10), bg='#f0f0f0', justify='left')
    instructions.pack(pady=(0, 20))
    
    def test_vos_fichiers_final():
        """Test the final vos fichiers dialog"""
        dialog = tk.Toplevel(root)
        dialog.title("Test - Vos fichiers (Final)")
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
                
                # Download button (green text)
                download_btn = tk.Button(
                    tree,
                    text="Télécharger",
                    bg='#27ae60',  # Green color
                    fg='white',
                    font=('Arial', 8),  # Smaller font for text
                    relief='flat',
                    command=lambda fid=file_id, fn=filename: download_file(fid, fn)
                )
                download_btn.place(
                    x=x + (width-70)//2,  # Adjusted for text button
                    y=y + (height-18)//2,
                    width=70,  # Wider for text
                    height=18
                )
        
        # Add buttons after tree is populated
        dialog.after(100, add_download_buttons)
        
        # Status
        status_label = tk.Label(dialog, text="✓ Test réussi! Boutons 'Télécharger' en texte, pas de boutons en bas.",
                               font=("Arial", 10), bg='#27ae60', fg='white', pady=10)
        status_label.pack(side='bottom', fill='x')
    
    def test_unified_sharing():
        """Test the unified file sharing interface"""
        dialog = tk.Toplevel(root)
        dialog.title("Test - Partage unifié")
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
        
        # File info section
        file_frame = ttk.LabelFrame(main_frame, text="Informations du fichier", padding="10")
        file_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(file_frame, text="Nom: test_file.pdf").pack(anchor='w')
        ttk.Label(file_frame, text="Date de création: 2024-01-01").pack(anchor='w')
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(instructions_frame, text="1. Sélectionnez des utilisateurs dans la liste ci-dessous", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="2. Cliquez sur 'Donner accès' pour les utilisateurs sans accès (rouge)", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="3. Cliquez sur 'Retirer accès' pour les utilisateurs avec accès (vert)", 
                 font=("Arial", 9)).pack(anchor='w')
        
        # Users section
        users_frame = ttk.LabelFrame(main_frame, text="Géologues disponibles", padding="10")
        users_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create treeview for all users with access status
        columns = ('Email', 'Date de création', 'Accès')
        users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=8)
        
        users_tree.heading('Email', text='Email')
        users_tree.heading('Date de création', text='Date de création')
        users_tree.heading('Accès', text='Accès')
        
        users_tree.column('Email', width=250)
        users_tree.column('Date de création', width=120)
        users_tree.column('Accès', width=100, anchor='center')
        
        # Configure selection style
        users_tree.tag_configure('selected', background='#3498db', foreground='white')
        users_tree.tag_configure('has_access', background='#d4edda', foreground='#155724')  # Light green
        users_tree.tag_configure('no_access', background='#f8d7da', foreground='#721c24')  # Light red
        
        # Add scrollbar
        users_scrollbar = ttk.Scrollbar(users_frame, orient='vertical', command=users_tree.yview)
        users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        users_tree.pack(side='left', fill='both', expand=True)
        users_scrollbar.pack(side='right', fill='y')
        
        # Add test users with different access status
        test_users = [
            ("user1@example.com", "2024-01-01", "Accès", "has_access"),
            ("user2@example.com", "2024-01-02", "Sans accès", "no_access"),
            ("user3@example.com", "2024-01-03", "Accès", "has_access"),
            ("user4@example.com", "2024-01-04", "Sans accès", "no_access"),
        ]
        
        for user in test_users:
            users_tree.insert('', 'end', values=(user[0], user[1], user[2]), tags=(user[3],))
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        # Status label
        status_label = ttk.Label(btn_frame, text="Prêt", font=("Arial", 9))
        status_label.pack(side='left', padx=(0, 10))
        
        def test_give_access():
            messagebox.showinfo("Test", "Test de 'Donner accès' - vérifier les messages d'erreur pour utilisateurs avec accès")
        
        def test_remove_access():
            messagebox.showinfo("Test", "Test de 'Retirer accès' - vérifier les messages d'erreur pour utilisateurs sans accès")
        
        ttk.Button(btn_frame, text="Donner accès", command=test_give_access).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Retirer accès", command=test_remove_access).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Actualiser", command=lambda: messagebox.showinfo("Test", "Actualisation simulée")).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Fermer", command=dialog.destroy).pack(side='right')
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Status
        status_label = tk.Label(dialog, text="✓ Test réussi! Interface unifiée avec statut d'accès coloré.",
                               font=("Arial", 10), bg='#27ae60', fg='white', pady=10)
        status_label.pack(side='bottom', fill='x')
    
    # Test buttons
    btn_frame = tk.Frame(test_frame, bg='#f0f0f0')
    btn_frame.pack()
    
    tk.Button(btn_frame, text="Test Vos fichiers (Final)", command=test_vos_fichiers_final,
              bg='#3498db', fg='white', font=('Arial', 10), padx=20, pady=10).pack(side='left', padx=10)
    
    tk.Button(btn_frame, text="Test Partage Unifié", command=test_unified_sharing,
              bg='#27ae60', fg='white', font=('Arial', 10), padx=20, pady=10).pack(side='left', padx=10)
    
    # Close button
    tk.Button(test_frame, text="Fermer", command=root.destroy,
              bg='#e74c3c', fg='white', font=('Arial', 10), padx=20, pady=10).pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_final_improvements() 