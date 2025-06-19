import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Treeview
from core import crypto
import requests
from .user_management_dialog import show_create_user_dialog

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
    label = tk.Label(parent, text="Gestion", font=(None, 14))
    label.grid(row=7, column=0, sticky="w", pady=(30, 5))
    hr = tk.Frame(parent, height=2, bg='black')
    hr.grid(row=8, column=0, sticky='ew', pady=(0, 10))

    # Container for buttons
    frame = tk.Frame(parent)
    frame.grid(row=9, column=0, sticky='w')

    def make_btn(parent, text, icon, command):
        btn = tk.Frame(
            parent,
            width=button_size,
            height=button_size,
            relief='raised',
            borderwidth=2,
            cursor='hand2'
        )
        btn.grid_propagate(False)
        icon_label = tk.Label(btn, text=icon, font=("Arial", 48), fg="gray")
        icon_label.pack(expand=True)
        txt_label = tk.Label(btn, text=text)
        txt_label.pack(side='bottom', pady=10)
        for w in (btn, icon_label, txt_label):
            w.bind("<Button-1>", lambda e: command())
        return btn

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
                        "Oui" if user['is_admin'] else "Non"
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
            response = requests.get('https://127.0.0.1:5000/api/admin/users', headers=headers, verify=False)
            if response.status_code == 200:
                users = response.json().get('users', [])
                win = tk.Toplevel()
                win.title("Gestion des utilisateurs")
                win.geometry("800x500")
                win.configure(bg='#f0f0f0')
                
                # Main container
                main_frame = tk.Frame(win)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                # Header with title and create button
                header_frame = tk.Frame(main_frame)
                header_frame.pack(fill='x', pady=(0, 20))
                
                title_label = tk.Label(header_frame, text="Liste des utilisateurs", 
                                      font=("Arial", 16, "bold"))
                title_label.pack(side='left')
                
                def create_user_callback():
                    result = show_create_user_dialog(win, jwt_token_global)
                    if result:
                        refresh_users_table(tree)
                
                create_btn = tk.Button(header_frame, text="Créer un compte", 
                                       command=create_user_callback, fg='white')
                create_btn.pack(side='right')
                
                # Create Treeview for table
                tree = Treeview(main_frame, columns=('id','email','admin','actions'), show='headings', height=15)
                
                tree.heading('id', text='ID')
                tree.heading('email', text='Email')
                tree.heading('admin', text='Administrateur')
                tree.heading('actions', text='Actions')
                
                tree.column('id', width=80, anchor='center')
                tree.column('email', width=300, anchor='w')
                tree.column('admin', width=120, anchor='center')
                tree.column('actions', width=100, anchor='center')
                
                scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                for user in users:
                    tree.insert('', 'end', values=(
                        user['id'],
                        user['email'],
                        "Oui" if user['is_admin'] else "Non"
                    ))

                def add_delete_buttons():
                    for item in tree.get_children():
                        user_id, user_email, *_ = tree.item(item, 'values')
                        delete_btn = tk.Button(tree, text="Supprimer", 
                                              bg='#e74c3c', fg='white', 
                                              font=('Arial', 9),
                                              relief='flat',
                                              command=lambda uid=user_id, email=user_email: delete_user(uid, email, tree))
                        tree.set(item, 'actions', '')
                        bbox = tree.bbox(item, 'actions')
                        if bbox:
                            delete_btn.place(x=bbox[0] + 10, y=bbox[1] + 5, width=80, height=30)
                
                win.after(100, add_delete_buttons)
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des utilisateurs: {response.text}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")

    def handle_2():
        print("hello")

    # Role-based button logic
    if role == "Geophysicien":
        dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
        dec_btn.grid(row=0, column=0)
    elif role == "Responsable":
        dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
        dec_btn.grid(row=0, column=0, padx=(0, 10))
        enc_btn = make_btn(frame, "Gestions d'utilisateurs", "👤", handle_1)
        enc_btn.grid(row=0, column=1)
