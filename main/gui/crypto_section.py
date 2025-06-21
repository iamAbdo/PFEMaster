import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import crypto
import os
from PIL import Image, ImageTk
from utils.auth_state import get_jwt_token_global
import requests

def create_crypto_section(parent, button_size):
    # Label and divider
    label = tk.Label(parent, text="Cryptographie", font=("Arial", 14))
    label.grid(row=3, column=0, sticky="w", pady=(30, 5))
    hr = ttk.Separator(parent, orient='horizontal')
    hr.grid(row=4, column=0, sticky='ew', pady=(0, 10))

    # Container for buttons
    frame = ttk.Frame(parent)
    frame.grid(row=5, column=0, sticky='w')

    def load_icon(path, size):
        if os.path.exists(path):
            img = Image.open(path).resize((int(size*0.45), int(size*0.45)), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        return None

    def make_btn(parent, text, emoji, command):
        btn_height = button_size
        btn_width = int(button_size * 2.2)
        btn = tk.Frame(parent, width=btn_width, height=btn_height, bg="#f7c97c", relief='raised', borderwidth=2, cursor='hand2')
        btn.grid_propagate(False)
        icon_label = tk.Label(btn, text=emoji, font=("Arial", int(btn_height*0.4)), fg="gray", bg="#f7c97c")
        icon_label.pack(expand=True)
        txt_label = tk.Label(btn, text=text, bg="#f7c97c")
        txt_label.pack(side='bottom', pady=10)
        for w in (btn, icon_label, txt_label):
            w.bind("<Button-1>", lambda e: command())
        return btn

    def handle_encrypt():
        # Check if user is authenticated
        if not get_jwt_token_global():
            messagebox.showerror("Erreur", "Vous devez être connecté pour chiffrer des fichiers")
            return
        
        filepath = filedialog.askopenfilename(
            title="Sélectionner un fichier à chiffrer",
            filetypes=[("Tous les fichiers", "*.*"), ("Fichiers PDF", "*.pdf"), ("Fichiers texte", "*.txt")]
        )
        if filepath:
            crypto.encrypt_file(filepath)

    def handle_decrypt():
        # Check if user is authenticated
        if not get_jwt_token_global():
            messagebox.showerror("Erreur", "Vous devez être connecté pour déchiffrer des fichiers")
            return
        
        filepath = filedialog.askopenfilename(
            title="Sélectionner un fichier à déchiffrer",
            filetypes=[("Fichiers chiffrés", "*.enc"), ("Tous les fichiers", "*.*")]
        )
        if filepath:
            crypto.decrypt_file(filepath)

    def handle_my_files():
        # Check if user is authenticated
        if not get_jwt_token_global():
            messagebox.showerror("Erreur", "Vous devez être connecté pour accéder à vos fichiers")
            return
        
        files = crypto.get_user_files()
        if files:
            show_files_dialog(files)
        else:
            messagebox.showinfo("Information", "Aucun fichier PDF exporté trouvé")

    def show_files_dialog(files):
        """Show a dialog with user's files"""
        dialog = tk.Toplevel()
        dialog.title("Vos fichiers PDF")
        dialog.geometry("800x500")
        dialog.configure(bg='#f0f0f0')
        dialog.resizable(True, True)  # Make resizable
        dialog.minsize(700, 400)  # Set minimum size
        dialog.transient(parent)
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
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
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
        tree.column('Actions', width=150, anchor='center')  # Increased width for multiple buttons
        
        # Configure row styling
        tree.tag_configure('evenrow', background='#f9f9f9')
        tree.tag_configure('oddrow', background='#ffffff')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Populate treeview
        file_data_dict = {}  # Dictionary to store file data by item ID
        for idx, file in enumerate(files):
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
            try:
                jwt_token = get_jwt_token_global()
                headers = {'Authorization': f'Bearer {jwt_token}'}
                
                response = requests.get(
                    f'https://127.0.0.1:5000/api/user/files/{file_id}/download',
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 200:
                    # Ask user where to save the file
                    save_path = filedialog.asksaveasfilename(
                        title="Enregistrer le fichier",
                        defaultextension=".pdf"
                    )
                    
                    if save_path:
                        with open(save_path, 'wb') as f:
                            f.write(response.content)
                        messagebox.showinfo("Succès", f"Fichier téléchargé: {os.path.basename(save_path)}")
                else:
                    messagebox.showerror("Erreur", "Impossible de télécharger le fichier")
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du téléchargement: {str(e)}")
        
        def delete_file(file_id, filename):
            """Delete a file (only for owned files)"""
            result = messagebox.askyesno("Confirmation", 
                                       f"Êtes-vous sûr de vouloir supprimer le fichier {filename}?")
            if not result:
                return
            
            try:
                jwt_token = get_jwt_token_global()
                headers = {'Authorization': f'Bearer {jwt_token}'}
                
                response = requests.delete(
                    f'https://127.0.0.1:5000/api/user/files/{file_id}',
                    headers=headers,
                    verify=False
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("Succès", "Fichier supprimé avec succès!")
                    refresh_files()
                else:
                    error_message = response.json().get('error', 'Erreur inconnue')
                    messagebox.showerror("Erreur", error_message)
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer le fichier: {e}")
        
        def refresh_files():
            """Refresh the files list"""
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            file_data_dict.clear()
            
            # Reload files
            files = crypto.get_user_files()
            if files:
                for idx, file in enumerate(files):
                    tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                    file_type = "Propriétaire" if file.get('is_owner', False) else "Partagé"
                    created_date = file.get('created_at', '').split('T')[0] if file.get('created_at') else ''
                    owner = file.get('owner', 'Vous') if not file.get('is_owner', False) else 'Vous'
                    
                    item_id = tree.insert('', 'end', values=(
                        file.get('filename', ''),
                        file_type,
                        created_date,
                        owner,
                        ''
                    ), tags=(tag,))
                    file_data_dict[item_id] = file
                
                # Re-add buttons after refresh
                dialog.after(100, add_download_buttons)
            else:
                messagebox.showinfo("Information", "Aucun fichier PDF exporté trouvé")
        
        def add_download_buttons():
            """Add download and delete buttons to each row"""
            for item in tree.get_children():
                file_data = file_data_dict.get(item)
                if not file_data:
                    continue
                    
                file_id = file_data.get('id')
                filename = file_data.get('filename', '')
                is_owner = file_data.get('is_owner', False)
                
                bbox = tree.bbox(item, 'Actions')
                if not bbox:
                    continue
                
                x, y, width, height = bbox
                
                # Download button (green)
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
                    x=x + 2,
                    y=y + (height-18)//2,
                    width=70,  # Wider for text
                    height=18
                )
                
                # Delete button (red) - only for owned files
                if is_owner:
                    delete_btn = tk.Button(
                        tree,
                        text="Supprimer",
                        bg='#e74c3c',  # Red color
                        fg='white',
                        font=('Arial', 8),
                        relief='flat',
                        command=lambda fid=file_id, fn=filename: delete_file(fid, fn)
                    )
                    delete_btn.place(
                        x=x + 75,  # Position next to download button
                        y=y + (height-18)//2,
                        width=70,
                        height=18
                    )
        
        # Add buttons after tree is populated
        dialog.after(100, add_download_buttons)

    base_dir = os.path.dirname(__file__)
    enc_btn = make_btn(frame, "Chiffrer", "🔒", handle_encrypt)
    enc_btn.grid(row=0, column=0, padx=(0, 10))
    
    dec_btn = make_btn(frame, "Déchiffrer", "🔓", handle_decrypt)
    dec_btn.grid(row=0, column=1, padx=(0, 10))
    
    files_btn = make_btn(frame, "Vos fichiers", "📁", handle_my_files)
    files_btn.grid(row=0, column=2)
