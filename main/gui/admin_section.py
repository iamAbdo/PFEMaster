import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Treeview
from tkinter import ttk
from core import crypto
import requests
from .user_management_dialog import show_create_user_dialog
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
            win.geometry("800x500")
            win.configure(bg='#f0f0f0')

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
                columns=('id','email','role','actions'),
                show='headings',
                height=15
            )
            # headings
            tree.heading('id', text='ID')
            tree.heading('email', text='Email')
            tree.heading('role', text='Rôle')
            tree.heading('actions', text='Actions')
            # column widths
            tree.column('id', width=80, anchor='center')
            tree.column('email', width=300, anchor='w')
            tree.column('role', width=120, anchor='center')
            tree.column('actions', width=100, anchor='center')

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
                        user['id'],
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
                        font=('Arial', 9),
                        relief='flat',
                        padx=5,
                        pady=2,
                        command=lambda uid=user_id, email=user_email: delete_user(uid, email, tree)
                    )
                    # shrink to fit the rowheight
                    btn.place(
                        x=x + (width-70)//2,
                        y=y + (height-20)//2,
                        width=70,
                        height=20
                    )

            # give the tree time to render before placing buttons
            win.after(100, add_delete_buttons)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")

    def handle_2():
        print("hello")

    base_dir = os.path.dirname(__file__)
    if role == "Geophysicien":
        dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
        dec_btn.grid(row=0, column=0)
    elif role == "Responsable":
        dec_btn = make_btn(frame, "Gestions des zones", "🌐", handle_2)
        dec_btn.grid(row=0, column=0, padx=(0, 10))
        enc_btn = make_btn(frame, "Gestions d'utilisateurs", "👤", handle_1)
        enc_btn.grid(row=0, column=1)
