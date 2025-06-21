import tkinter as tk
from tkinter import ttk, messagebox
import requests
from utils.auth_state import get_jwt_token_global

class FileSharingDialog:
    def __init__(self, parent, file_info):
        self.parent = parent
        self.file_info = file_info
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Partage de fichier: {file_info.get('filename', '')}")
        self.dialog.geometry("700x500")  # Reduced from larger size
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(True, True)  # Make resizable
        self.dialog.minsize(600, 400)  # Set minimum size
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"700x500+{x}+{y}")
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Create a canvas with scrollbar for the main content
        canvas = tk.Canvas(self.dialog, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
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
        
        ttk.Label(file_frame, text=f"Nom: {self.file_info.get('filename', '')}").pack(anchor='w')
        ttk.Label(file_frame, text=f"Date de création: {self.file_info.get('created_at', '').split('T')[0]}").pack(anchor='w')
        
        # Instructions
        instructions_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instructions_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(instructions_frame, text="1. Sélectionnez des utilisateurs dans la liste ci-dessous", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="2. Cliquez sur 'Donner accès' pour les utilisateurs sans accès (rouge)", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="3. Cliquez sur 'Retirer accès' pour les utilisateurs avec accès (vert)", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="4. Vous pouvez partager avec des Geologues et des Géophysiciens", 
                 font=("Arial", 9)).pack(anchor='w')
        ttk.Label(instructions_frame, text="5. Le propriétaire du fichier est affiché en gris et ne peut pas être sélectionné", 
                 font=("Arial", 9)).pack(anchor='w')
        
        # Users section
        users_frame = ttk.LabelFrame(main_frame, text="Utilisateurs disponibles (Geologues et Géophysiciens)", padding="10")
        users_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create treeview for all users with access status
        columns = ('Email', 'Rôle', 'Date de création', 'Accès')
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=12)
        
        self.users_tree.heading('Email', text='Email')
        self.users_tree.heading('Rôle', text='Rôle')
        self.users_tree.heading('Date de création', text='Date de création')
        self.users_tree.heading('Accès', text='Accès')
        
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Rôle', width=100, anchor='center')
        self.users_tree.column('Date de création', width=120)
        self.users_tree.column('Accès', width=100, anchor='center')
        
        # Configure selection style
        self.users_tree.tag_configure('selected', background='#3498db', foreground='white')
        self.users_tree.tag_configure('has_access', background='#d4edda', foreground='#155724')  # Light green
        self.users_tree.tag_configure('no_access', background='#f8d7da', foreground='#721c24')  # Light red
        self.users_tree.tag_configure('owner', background='#e9ecef', foreground='#6c757d')  # Gray for owner
        
        # Add scrollbar
        users_scrollbar = ttk.Scrollbar(users_frame, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.pack(side='left', fill='both', expand=True)
        users_scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(btn_frame, text="Prêt", font=("Arial", 9))
        self.status_label.pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Donner accès", command=self.give_access).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Retirer accès", command=self.remove_access).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Actualiser", command=self.load_data).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Fermer", command=self.dialog.destroy).pack(side='right')
        
        # Bind selection events
        self.users_tree.bind('<<TreeviewSelect>>', self.on_users_selection)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Unbind mouse wheel when dialog is destroyed
        def _on_destroy():
            canvas.unbind_all("<MouseWheel>")
        
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: [_on_destroy(), self.dialog.destroy()])

    def load_data(self):
        """Load all users with their access status"""
        try:
            jwt_token = get_jwt_token_global()
            headers = {'Authorization': f'Bearer {jwt_token}'}
            
            # Get all users for sharing (including owner)
            response = requests.get(
                f'https://127.0.0.1:5000/api/user/files/{self.file_info.get("id")}/users-for-sharing',
                headers=headers,
                verify=False
            )
            
            if response.status_code != 200:
                messagebox.showerror("Erreur", "Impossible de charger les utilisateurs")
                return
            
            data = response.json()
            users_for_sharing = data.get('users_for_sharing', [])
            
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Add all users with their access status
            for user in users_for_sharing:
                created_date = user.get('created_at', '').split('T')[0] if user.get('created_at') else ''
                user_id = user.get('id')
                is_owner = user.get('is_owner', False)
                has_access = user.get('has_access', False)
                
                if is_owner:
                    access_text = "Propriétaire"
                    access_tag = 'owner'
                else:
                    access_text = "Accès" if has_access else "Sans accès"
                    access_tag = 'has_access' if has_access else 'no_access'
                
                self.users_tree.insert('', 'end', values=(
                    user.get('email', ''),
                    user.get('role', ''),
                    created_date,
                    access_text
                ), tags=(user_id, access_tag))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")

    def load_available_users(self):
        """This method is no longer needed - kept for compatibility"""
        pass

    def load_shared_users(self):
        """This method is no longer needed - kept for compatibility"""
        pass

    def give_access(self):
        """Give access to selected users"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner des utilisateurs à donner accès")
            return
        
        # Filter out owner rows from selection
        valid_selections = []
        for item in selected:
            tags = self.users_tree.item(item, 'tags')
            if 'owner' not in tags:  # Don't process owner
                valid_selections.append(item)
        
        if not valid_selections:
            messagebox.showwarning("Attention", "Veuillez sélectionner des utilisateurs à donner accès")
            return
        
        # Check if any selected users already have access
        users_to_give_access = []
        users_already_have_access = []
        
        for item in valid_selections:
            user_id = self.users_tree.item(item, 'tags')[0]
            values = self.users_tree.item(item, 'values')
            access_status = values[3] if len(values) > 3 else "Sans accès"
            email = values[0] if len(values) > 0 else "Unknown"
            
            if access_status == "Accès":
                users_already_have_access.append(email)
            else:
                users_to_give_access.append(int(user_id))
        
        # Show warning for users who already have access
        if users_already_have_access:
            messagebox.showwarning("Attention", 
                                 f"Les utilisateurs suivants ont déjà accès:\n" + 
                                 "\n".join(users_already_have_access))
        
        # If no users to give access to, return
        if not users_to_give_access:
            return
        
        try:
            jwt_token = get_jwt_token_global()
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            share_data = {'user_ids': users_to_give_access}
            
            response = requests.post(
                f'https://127.0.0.1:5000/api/user/files/{self.file_info.get("id")}/share',
                json=share_data,
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Succès", f"Accès donné à {len(data.get('shared_with', []))} utilisateur(s)")
                self.load_data()  # Refresh the list
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', 'Erreur inconnue')
                except:
                    error_message = response.text
                messagebox.showerror("Erreur", f"Erreur lors de la donnation d'accès: {error_message}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la donnation d'accès: {str(e)}")

    def remove_access(self):
        """Remove access for selected users"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner des utilisateurs à retirer")
            return
        
        # Filter out owner rows from selection
        valid_selections = []
        for item in selected:
            tags = self.users_tree.item(item, 'tags')
            if 'owner' not in tags:  # Don't process owner
                valid_selections.append(item)
        
        if not valid_selections:
            messagebox.showwarning("Attention", "Veuillez sélectionner des utilisateurs à retirer")
            return
        
        # Check if any selected users don't have access
        users_to_remove_access = []
        users_no_access = []
        
        for item in valid_selections:
            user_id = self.users_tree.item(item, 'tags')[0]
            values = self.users_tree.item(item, 'values')
            access_status = values[3] if len(values) > 3 else "Sans accès"
            email = values[0] if len(values) > 0 else "Unknown"
            
            if access_status == "Sans accès":
                users_no_access.append(email)
            else:
                users_to_remove_access.append(int(user_id))
        
        # Show warning for users who don't have access
        if users_no_access:
            messagebox.showwarning("Attention", 
                                 f"Les utilisateurs suivants n'ont pas accès:\n" + 
                                 "\n".join(users_no_access))
        
        # If no users to remove access from, return
        if not users_to_remove_access:
            return
        
        try:
            jwt_token = get_jwt_token_global()
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'https://127.0.0.1:5000/api/user/files/{self.file_info.get("id")}/unshare',
                json={'user_ids': users_to_remove_access},
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Succès", f"Accès retiré pour {len(data.get('removed_from', []))} utilisateur(s)")
                self.load_data()  # Refresh the list
            else:
                error_data = response.json()
                messagebox.showerror("Erreur", error_data.get('error', 'Erreur inconnue'))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du retrait d'accès: {str(e)}")

    def on_users_selection(self, event):
        """Handle selection in users tree"""
        selected = self.users_tree.selection()
        if selected:
            # Filter out owner rows from selection
            valid_selections = []
            for item in selected:
                tags = self.users_tree.item(item, 'tags')
                if 'owner' not in tags:  # Don't allow selection of owner
                    valid_selections.append(item)
                else:
                    # Remove owner from selection
                    self.users_tree.selection_remove(item)
            
            # Update selection count
            count = len(valid_selections)
            if count > 0:
                self.status_label.config(text=f"{count} utilisateur(s) sélectionné(s)")
            else:
                self.status_label.config(text="Prêt")
        else:
            self.status_label.config(text="Prêt")

    def show(self):
        """Show the dialog and wait for it to close"""
        self.dialog.wait_window()
        return self.result


def show_file_sharing_dialog(parent, file_info):
    """Show the file sharing dialog"""
    return FileSharingDialog(parent, file_info).show() 