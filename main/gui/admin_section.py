import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Treeview
from tkinter import ttk
from core import crypto
import requests
from .user_management_dialog import show_create_user_dialog
from .file_sharing_dialog import show_file_sharing_dialog
import os
from PIL import Image, ImageTk

# Global variable to store JWT token
jwt_token_global = None

def set_jwt_token(token):
    global jwt_token_global
    jwt_token_global = token

def create_admin_section(parent, button_size, jwt_token=None, role=None):
    global jwt_token_global
    if jwt_token:
        jwt_token_global = jwt_token
    
    # Label and divider
    label = tk.Label(parent, text="Gestion", font=('Arial', 14))
    label.grid(row=7, column=0, sticky="w", pady=(30, 5))
    hr = tk.Frame(parent, height=2, bg='black')
    hr.grid(row=8, column=0, sticky='ew', pady=(0, 10))

    # Container for buttons
    frame = tk.Frame(parent)
    frame.grid(row=9, column=0, sticky='w')

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

    def handle_file_access_management():
        """Handle file access management for all PDFs"""
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            
            # Get all files in the system (admin endpoint)
            response = requests.get(
                'https://127.0.0.1:5000/api/user/admin/files',
                headers=headers,
                verify=False
            )
            
            if response.status_code != 200:
                messagebox.showerror(
                    "Erreur",
                    f"Erreur lors de la récupération des fichiers: {response.text}"
                )
                return

            files_data = response.json()
            all_files = files_data.get('files', [])
            
            if not all_files:
                messagebox.showinfo("Information", "Aucun fichier PDF trouvé")
                return

            # Create file management window
            win = tk.Toplevel()
            win.title("Gestion d'accès aux fichiers")
            win.geometry("800x500")  # Reduced from 900x600
            win.configure(bg='#f0f0f0')
            win.resizable(True, True)  # Make window resizable
            win.minsize(700, 400)  # Set minimum size

            # Main container
            main_frame = tk.Frame(win, bg='#f0f0f0')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)

            # Header
            header_frame = tk.Frame(main_frame, bg='#f0f0f0')
            header_frame.pack(fill='x', pady=(0, 20))

            tk.Label(
                header_frame,
                text="Gestion d'accès aux fichiers PDF",
                font=("Arial", 16, "bold"),
                bg='#f0f0f0'
            ).pack(side='left')

            # Style the Treeview
            style = ttk.Style(win)
            style.configure(
                "File.Treeview",
                rowheight=32,
                font=('Arial', 11),
                fieldbackground='white',
                bordercolor='#ccc',
                borderwidth=1
            )
            style.configure(
                "File.Treeview.Heading",
                font=('Arial', 12, 'bold'),
                relief='flat'
            )
            style.layout("File.Treeview", [
                ('File.Treeview.treearea', {'sticky': 'nswe'})
            ])

            # Create treeview
            tree = Treeview(
                main_frame,
                style="File.Treeview",
                columns=('filename', 'type', 'created_at', 'owner', 'actions'),
                show='headings',
                height=15
            )
            
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

            tree.tag_configure('evenrow', background='#f9f9f9')
            tree.tag_configure('oddrow', background='#ffffff')

            # Scrollbar
            scrollbar = tk.Scrollbar(
                main_frame,
                orient='vertical',
                command=tree.yview
            )
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # Populate treeview
            file_data_dict = {}  # Dictionary to store file data by item ID
            for idx, file in enumerate(all_files):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                file_type = "Propriétaire" if file.get('is_owner', False) else "Partagé"
                created_date = file.get('created_at', '').split('T')[0] if file.get('created_at') else ''
                owner = file.get('owner', 'Vous') if not file.get('is_owner', False) else 'Vous'
                
                item_id = tree.insert(
                    '',
                    'end',
                    values=(
                        file.get('filename', ''),
                        file_type,
                        created_date,
                        owner,
                        ''  # placeholder for buttons
                    ),
                    tags=(tag,)
                )
                file_data_dict[item_id] = file

            def download_file(file_id, filename):
                """Download a file"""
                try:
                    response = requests.get(
                        f'https://127.0.0.1:5000/api/user/files/{file_id}/download',
                        headers=headers,
                        verify=False
                    )
                    
                    if response.status_code == 200:
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
                """Delete a file"""
                result = messagebox.askyesno("Confirmation", 
                                           f"Êtes-vous sûr de vouloir supprimer le fichier {filename}?")
                if not result:
                    return
                
                try:
                    response = requests.delete(
                        f'https://127.0.0.1:5000/api/user/files/{file_id}',
                        headers=headers,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        messagebox.showinfo("Succès", "Fichier supprimé avec succès!")
                        refresh_files_table()
                    else:
                        error_message = response.json().get('error', 'Erreur inconnue')
                        messagebox.showerror("Erreur", error_message)
                        
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de supprimer le fichier: {e}")

            def share_file(file_data):
                """Share a file"""
                show_file_sharing_dialog(win, file_data)

            def refresh_files_table():
                """Refresh the files table"""
                for item in tree.get_children():
                    tree.delete(item)
                
                file_data_dict.clear()  # Clear the dictionary
                
                try:
                    response = requests.get(
                        'https://127.0.0.1:5000/api/user/admin/files',
                        headers=headers,
                        verify=False
                    )
                    
                    if response.status_code == 200:
                        files_data = response.json()
                        all_files = files_data.get('files', [])
                        
                        for idx, file in enumerate(all_files):
                            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                            file_type = "Propriétaire" if file.get('is_owner', False) else "Partagé"
                            created_date = file.get('created_at', '').split('T')[0] if file.get('created_at') else ''
                            owner = file.get('owner', 'Vous') if not file.get('is_owner', False) else 'Vous'
                            
                            item_id = tree.insert(
                                '',
                                'end',
                                values=(
                                    file.get('filename', ''),
                                    file_type,
                                    created_date,
                                    owner,
                                    ''
                                ),
                                tags=(tag,)
                            )
                            file_data_dict[item_id] = file
                        
                        # Re-add buttons after refresh
                        win.after(100, add_action_buttons)
                        
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de rafraîchir les données: {e}")

            def add_action_buttons():
                """Add action buttons to each row"""
                for item in tree.get_children():
                    file_data = file_data_dict.get(item)
                    if not file_data:
                        continue
                        
                    file_id = file_data.get('id')
                    filename = file_data.get('filename', '')
                    
                    bbox = tree.bbox(item, 'actions')
                    if not bbox:
                        continue
                    
                    x, y, width, height = bbox
                    
                    # Download button (always available for admin)
                    download_btn = tk.Button(
                        tree,
                        text="Télécharger",
                        bg='#3498db',
                        fg='white',
                        font=('Arial', 7),
                        relief='flat',
                        command=lambda fid=file_id, fn=filename: download_file(fid, fn)
                    )
                    download_btn.place(
                        x=x + 2,
                        y=y + (height-18)//2,
                        width=60,
                        height=18
                    )
                    
                    # Share button (admin can share any file)
                    share_btn = tk.Button(
                        tree,
                        text="Partager",
                        bg='#27ae60',
                        fg='white',
                        font=('Arial', 7),
                        relief='flat',
                        command=lambda fd=file_data: share_file(fd)
                    )
                    share_btn.place(
                        x=x + 65,
                        y=y + (height-18)//2,
                        width=50,
                        height=18
                    )
                    
                    # Delete button (admin can delete any file)
                    delete_btn = tk.Button(
                        tree,
                        text="Supprimer",
                        bg='#e74c3c',
                        fg='white',
                        font=('Arial', 7),
                        relief='flat',
                        command=lambda fid=file_id, fn=filename: delete_file(fid, fn)
                    )
                    delete_btn.place(
                        x=x + 118,
                        y=y + (height-18)//2,
                        width=50,
                        height=18
                    )

            # Add buttons after tree is populated
            win.after(100, add_action_buttons)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")

    def refresh_users_table(tree):
        """Refresh the users table with latest data"""
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            response = requests.get('https://127.0.0.1:5000/api/admin/users', headers=headers, verify=False)
            if response.status_code == 200:
                users = response.json().get('users', [])
                for user in users:
                    tree.insert('', 'end', values=(
                        user['id'],
                        user['email'],
                        user.get('role', '')
                    ))
                for i, item in enumerate(tree.get_children()):
                    if i % 2 == 0:
                        tree.item(item, tags=('evenrow',))
                    else:
                        tree.item(item, tags=('oddrow',))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de rafraîchir les données: {e}")

    def delete_user(user_id, user_email, tree):
        """Delete a user"""
        result = messagebox.askyesno("Confirmation", 
                                   f"Êtes-vous sûr de vouloir supprimer l'utilisateur {user_email}?")
        if not result:
            return
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            response = requests.delete(
                f'https://127.0.0.1:5000/api/user-management/delete-user/{user_id}',
                headers=headers,
                verify=False
            )
            if response.status_code == 200:
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès!")
                refresh_users_table(tree)
            else:
                error_message = response.json().get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_message)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer l'utilisateur: {e}")

    def handle_1():
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            response = requests.get(
                'https://127.0.0.1:5000/api/admin/users',
                headers=headers,
                verify=False
            )
            if response.status_code != 200:
                messagebox.showerror(
                    "Erreur",
                    f"Erreur lors de la récupération des utilisateurs: {response.text}"
                )
                return

            users = response.json().get('users', [])
            win = tk.Toplevel()
            win.title("Gestion des utilisateurs")
            win.geometry("700x450")  # Reduced from 800x500
            win.configure(bg='#f0f0f0')
            win.resizable(True, True)  # Make resizable
            win.minsize(600, 350)  # Set minimum size

            # Main container
            main_frame = tk.Frame(win, bg='#f0f0f0')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)

            # Header with title and create button
            header_frame = tk.Frame(main_frame, bg='#f0f0f0')
            header_frame.pack(fill='x', pady=(0, 20))

            tk.Label(
                header_frame,
                text="Liste des utilisateurs",
                font=("Arial", 16, "bold"),
                bg='#f0f0f0'
            ).pack(side='left')

            def create_user_callback():
                result = show_create_user_dialog(win, jwt_token_global)
                if result:
                    refresh_users_table(tree)

            tk.Button(
                header_frame,
                text="Créer un compte",
                command=create_user_callback,
                fg='white',
                bg='#3498db',
                relief='flat',
                padx=10, pady=5
            ).pack(side='right')

            # Style the Treeview for stripes & separators
            style = ttk.Style(win)
            style.configure(
                "Custom.Treeview",
                rowheight=32,
                font=('Arial', 11),
                fieldbackground='white',
                bordercolor='#ccc',
                borderwidth=1
            )
            style.configure(
                "Custom.Treeview.Heading",
                font=('Arial', 12, 'bold'),
                relief='flat'
            )
            # only show the tree area (no borders around)
            style.layout("Custom.Treeview", [
                ('Custom.Treeview.treearea', {'sticky': 'nswe'})
            ])

            tree = Treeview(
                main_frame,
                style="Custom.Treeview",
                columns=('email','role','actions'),
                show='headings',
                height=15
            )
            # headings
            # tree.heading('id', text='ID')
            tree.heading('email', text='Email')
            tree.heading('role', text='Rôle')
            tree.heading('actions', text='Actions')
            # column widths
            # tree.column('id', width=80, anchor='center')
            tree.column('email', width=250, anchor='w')  # Reduced from 300
            tree.column('role', width=100, anchor='center')  # Reduced from 120
            tree.column('actions', width=80, anchor='center')  # Reduced from 100

            # striped rows
            tree.tag_configure('evenrow', background='#f9f9f9')
            tree.tag_configure('oddrow', background='#ffffff')

            # scrollbar
            scrollbar = tk.Scrollbar(
                main_frame,
                orient='vertical',
                command=tree.yview
            )
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # populate with stripes
            for idx, user in enumerate(users):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tree.insert(
                    '',
                    'end',
                    values=(
                        # user['id'],
                        user['email'],
                        user.get('role', ''),
                        ''  # placeholder for the button
                    ),
                    tags=(tag,)
                )

            def add_delete_buttons():
                """Place a small delete button neatly inside each 'actions' cell."""
                for item in tree.get_children():
                    user_id, user_email, *_ = tree.item(item, 'values')
                    bbox = tree.bbox(item, 'actions')
                    if not bbox:
                        continue
                    x, y, width, height = bbox
                    btn = tk.Button(
                        tree,
                        text="Supprimer",
                        bg='#e74c3c',
                        fg='white',
                        font=('Arial', 8),
                        relief='flat',
                        padx=3,
                        pady=1,
                        command=lambda uid=user_id, email=user_email: delete_user(uid, email, tree)
                    )
                    btn.place(
                        x=x + (width-60)//2,
                        y=y + (height-18)//2,
                        width=60,
                        height=18
                    )

            # give the tree time to render before placing buttons
            win.after(100, add_delete_buttons)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")

    def handle_2():
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            response = requests.get(
                'https://127.0.0.1:5000/api/zone/zones',
                headers=headers,
                verify=False
            )
            if response.status_code != 200:
                messagebox.showerror(
                    "Erreur",
                    f"Erreur lors de la récupération des zones: {response.text}"
                )
                return

            zones = response.json().get('zones', [])
            win = tk.Toplevel()
            win.title("Gestion des zones")
            win.geometry("700x450")  # Reduced from 800x500
            win.configure(bg='#f0f0f0')
            win.resizable(True, True)  # Make resizable
            win.minsize(600, 350)  # Set minimum size

            main_frame = tk.Frame(win, bg='#f0f0f0')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)

            header_frame = tk.Frame(main_frame, bg='#f0f0f0')
            header_frame.pack(fill='x', pady=(0, 20))

            tk.Label(
                header_frame,
                text="Liste des zones",
                font=("Arial", 16, "bold"),
                bg='#f0f0f0'
            ).pack(side='left')

            def add_zone_callback():
                add_win = tk.Toplevel(win)
                add_win.title("Ajouter une zone")
                # add_win.geometry("400x300")
                add_win.configure(bg='#f0f0f0')

                labels = ['Sigle', 'Puits', 'Bloc', 'Permis']
                entries = {}
                for i, label in enumerate(labels):
                    tk.Label(add_win, text=label, bg='#f0f0f0').grid(row=i, column=0, padx=10, pady=10, sticky='e')
                    entry = tk.Entry(add_win)
                    entry.grid(row=i, column=1, padx=10, pady=10)
                    entries[label.lower()] = entry

                def submit():
                    data = {k: v.get() for k, v in entries.items()}
                    if not all(data.values()):
                        messagebox.showerror("Erreur", "Tous les champs sont obligatoires.")
                        return
                    try:
                        headers = {}
                        if jwt_token_global:
                            headers['Authorization'] = f'Bearer {jwt_token_global}'
                        resp = requests.post(
                            'https://127.0.0.1:5000/api/zone/zones',
                            json=data,
                            headers=headers,
                            verify=False
                        )
                        if resp.status_code == 201:
                            messagebox.showinfo("Succès", "Zone ajoutée avec succès!")
                            add_win.destroy()
                            refresh_zones_table(tree)
                        else:
                            error_message = resp.json().get('error', 'Erreur inconnue')
                            messagebox.showerror("Erreur", error_message)
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Impossible d'ajouter la zone: {e}")

                tk.Button(add_win, text="Ajouter", command=submit, bg='#27ae60', fg='white').grid(row=5, column=0, columnspan=2, pady=20)

            tk.Button(
                header_frame,
                text="Ajouter une zone",
                command=add_zone_callback,
                fg='white',
                bg='#3498db',
                relief='flat',
                padx=10, pady=5
            ).pack(side='right')

            style = ttk.Style(win)
            style.configure(
                "Zone.Treeview",
                rowheight=32,
                font=('Arial', 11),
                fieldbackground='white',
                bordercolor='#ccc',
                borderwidth=1
            )
            style.configure(
                "Zone.Treeview.Heading",
                font=('Arial', 12, 'bold'),
                relief='flat'
            )
            style.layout("Zone.Treeview", [
                ('Zone.Treeview.treearea', {'sticky': 'nswe'})
            ])

            tree = Treeview(
                main_frame,
                style="Zone.Treeview",
                columns=('sigle','puits','bloc','permis','actions'),
                show='headings',
                height=15
            )
            tree.heading('sigle', text='Sigle')
            tree.heading('puits', text='Puits')
            tree.heading('bloc', text='Bloc')
            tree.heading('permis', text='Permis')
            tree.heading('actions', text='Actions')
            tree.column('sigle', width=100, anchor='center')  # Reduced from 120
            tree.column('puits', width=100, anchor='center')  # Reduced from 120
            tree.column('bloc', width=100, anchor='center')   # Reduced from 120
            tree.column('permis', width=100, anchor='center') # Reduced from 120
            tree.column('actions', width=80, anchor='center') # Reduced from 100

            tree.tag_configure('evenrow', background='#f9f9f9')
            tree.tag_configure('oddrow', background='#ffffff')

            scrollbar = tk.Scrollbar(
                main_frame,
                orient='vertical',
                command=tree.yview
            )
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            def refresh_zones_table(tree):
                for item in tree.get_children():
                    tree.delete(item)
                try:
                    headers = {}
                    if jwt_token_global:
                        headers['Authorization'] = f'Bearer {jwt_token_global}'
                    response = requests.get('https://127.0.0.1:5000/api/zone/zones', headers=headers, verify=False)
                    if response.status_code == 200:
                        zones = response.json().get('zones', [])
                        for idx, zone in enumerate(zones):
                            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                            tree.insert(
                                '',
                                'end',
                                values=(
                                    zone['sigle'],
                                    zone['puits'],
                                    zone['bloc'],
                                    zone['permis'],
                                    ''
                                ),
                                tags=(tag,)
                            )
                    for i, item in enumerate(tree.get_children()):
                        if i % 2 == 0:
                            tree.item(item, tags=('evenrow',))
                        else:
                            tree.item(item, tags=('oddrow',))
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de rafraîchir les zones: {e}")

            def delete_zone(sigle, puits, bloc, permis):
                # Find the zoneId by fetching all zones and matching
                try:
                    headers = {}
                    if jwt_token_global:
                        headers['Authorization'] = f'Bearer {jwt_token_global}'
                    response = requests.get('https://127.0.0.1:5000/api/zone/zones', headers=headers, verify=False)
                    if response.status_code == 200:
                        zones = response.json().get('zones', [])
                        for zone in zones:
                            if zone['sigle'] == sigle and zone['puits'] == puits and zone['bloc'] == bloc and zone['permis'] == permis:
                                zone_id = zone['zoneId']
                                break
                        else:
                            messagebox.showerror("Erreur", "Zone non trouvée.")
                            return
                    else:
                        messagebox.showerror("Erreur", "Impossible de trouver la zone à supprimer.")
                        return
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la recherche de la zone: {e}")
                    return
                result = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer la zone {sigle}?")
                if not result:
                    return
                try:
                    headers = {}
                    if jwt_token_global:
                        headers['Authorization'] = f'Bearer {jwt_token_global}'
                    resp = requests.delete(
                        f'https://127.0.0.1:5000/api/zone/zones/{zone_id}',
                        headers=headers,
                        verify=False
                    )
                    if resp.status_code == 200:
                        messagebox.showinfo("Succès", "Zone supprimée avec succès!")
                        refresh_zones_table(tree)
                    else:
                        error_message = resp.json().get('error', 'Erreur inconnue')
                        messagebox.showerror("Erreur", error_message)
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de supprimer la zone: {e}")

            for idx, zone in enumerate(zones):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tree.insert(
                    '',
                    'end',
                    values=(
                        zone['sigle'],
                        zone['puits'],
                        zone['bloc'],
                        zone['permis'],
                        ''
                    ),
                    tags=(tag,)
                )

            def add_delete_buttons():
                for item in tree.get_children():
                    sigle, puits, bloc, permis, *_ = tree.item(item, 'values')
                    bbox = tree.bbox(item, 'actions')
                    if not bbox:
                        continue
                    x, y, width, height = bbox
                    btn = tk.Button(
                        tree,
                        text="Supprimer",
                        bg='#e74c3c',
                        fg='white',
                        font=('Arial', 8),
                        relief='flat',
                        padx=3,
                        pady=1,
                        command=lambda s=sigle, p=puits, b=bloc, pm=permis: delete_zone(s, p, b, pm)
                    )
                    btn.place(
                        x=x + (width-60)//2,
                        y=y + (height-18)//2,
                        width=60,
                        height=18
                    )

            win.after(100, add_delete_buttons)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")

    base_dir = os.path.dirname(__file__)
    if role == "Geophysicien":
        dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
        dec_btn.grid(row=0, column=0)
    elif role == "Responsable":
        dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
        dec_btn.grid(row=0, column=0, padx=(0, 10))
        enc_btn = make_btn(frame, "Gestions d'utilisateurs", "👤", handle_1)
        enc_btn.grid(row=0, column=1, padx=(0, 10))
        access_btn = make_btn(frame, "Gestion d'accès", "🔐", handle_file_access_management)
        access_btn.grid(row=0, column=2)
