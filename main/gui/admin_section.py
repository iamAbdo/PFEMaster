import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import crypto
import requests
from .user_management_dialog import show_create_user_dialog

# Global variable to store JWT token
jwt_token_global = None

def set_jwt_token(token):
    global jwt_token_global
    jwt_token_global = token

def create_admin_section(parent, button_size, jwt_token=None):
    global jwt_token_global
    if jwt_token:
        jwt_token_global = jwt_token
    
    # Label and divider
    label = tk.Label(parent, text="Gestion", font=(None, 14))
    label.grid(row=7, column=0, sticky="w", pady=(30, 5))
    hr = ttk.Separator(parent, orient='horizontal')
    hr.grid(row=8, column=0, sticky='ew', pady=(0, 10))

    # Container for buttons
    frame = ttk.Frame(parent)
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
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
            
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            response = requests.get('https://127.0.0.1:5000/api/admin/users', headers=headers, verify=False)
            if response.status_code == 200:
                users = response.json().get('users', [])
                
                # Populate the table
                for user in users:
                    tree.insert('', 'end', values=(
                        user['id'],
                        user['email'],
                        "Oui" if user['is_admin'] else "Non"
                    ))
                    
                # Apply alternating row colors
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
                error_data = response.json()
                error_message = error_data.get('error', 'Erreur inconnue')
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
                main_frame = ttk.Frame(win)
                main_frame.pack(fill='both', expand=True, padx=20, pady=20)
                
                # Header with title and create button
                header_frame = ttk.Frame(main_frame)
                header_frame.pack(fill='x', pady=(0, 20))
                
                title_label = tk.Label(header_frame, text="Liste des utilisateurs", 
                                      font=("Arial", 16, "bold"))
                title_label.pack(side='left')
                
                def create_user_callback():
                    result = show_create_user_dialog(win, jwt_token_global)
                    if result:
                        refresh_users_table(tree)
                
                create_btn = ttk.Button(header_frame, text="Créer un compte", 
                                       command=create_user_callback)
                create_btn.pack(side='right')
                
                # Create Treeview for table
                columns = ('id', 'email', 'admin', 'actions')
                tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
                
                # Define headings
                tree.heading('id', text='ID')
                tree.heading('email', text='Email')
                tree.heading('admin', text='Administrateur')
                tree.heading('actions', text='Actions')
                
                # Configure column widths
                tree.column('id', width=80, anchor='center')
                tree.column('email', width=300, anchor='w')
                tree.column('admin', width=120, anchor='center')
                tree.column('actions', width=100, anchor='center')
                
                # Style the treeview
                style = ttk.Style()
                style.theme_use('clam')
                style.configure("Treeview", 
                               background="#ffffff",
                               foreground="#000000",
                               rowheight=40,
                               fieldbackground="#ffffff")
                style.configure("Treeview.Heading", 
                               background="#4a90e2",
                               foreground="white",
                               font=('Arial', 10, 'bold'))
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                # Pack treeview and scrollbar
                tree.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Populate the table
                for user in users:
                    tree.insert('', 'end', values=(
                        user['id'],
                        user['email'],
                        "Oui" if user['is_admin'] else "Non"
                    ))
                
                # Bind double-click event to show user details
                def on_double_click(event):
                    item = tree.selection()[0]
                    user_data = tree.item(item, 'values')
                    messagebox.showinfo("Détails utilisateur", 
                                       f"ID: {user_data[0]}\nEmail: {user_data[1]}\nAdmin: {user_data[2]}")
                
                tree.bind('<Double-1>', on_double_click)
                
                # Add some spacing and styling
                tree.tag_configure('oddrow', background='#f8f9fa')
                tree.tag_configure('evenrow', background='#ffffff')
                
                # Apply alternating row colors
                for i, item in enumerate(tree.get_children()):
                    if i % 2 == 0:
                        tree.item(item, tags=('evenrow',))
                    else:
                        tree.item(item, tags=('oddrow',))
                
                # Add delete buttons to each row
                def add_delete_buttons():
                    for item in tree.get_children():
                        values = tree.item(item, 'values')
                        user_id = values[0]
                        user_email = values[1]
                        
                        # Create delete button
                        delete_btn = tk.Button(tree, text="Supprimer", 
                                              bg='#e74c3c', fg='white', 
                                              font=('Arial', 9),
                                              relief='flat',
                                              command=lambda uid=user_id, email=user_email: delete_user(uid, email, tree))
                        
                        # Position the button in the actions column
                        tree.set(item, 'actions', '')
                        bbox = tree.bbox(item, 'actions')
                        if bbox:
                            delete_btn.place(x=bbox[0] + 10, y=bbox[1] + 5, width=80, height=30)
                
                # Call after a short delay to ensure tree is rendered
                win.after(100, add_delete_buttons)
                
            else:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des utilisateurs: {response.text}")
                print(response.text)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")
            print(e)

    def handle_2():
        print("hello")

    enc_btn = make_btn(frame, "Gestions d'utilisateurs", "👤", handle_1)
    enc_btn.grid(row=0, column=0, padx=(0, 10))
    dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
    dec_btn.grid(row=0, column=1)
