import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core import crypto
import requests

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

    def handle_1():
        try:
            headers = {}
            if jwt_token_global:
                headers['Authorization'] = f'Bearer {jwt_token_global}'
            response = requests.get('https://127.0.0.1:5000/api/admin/users', headers=headers, verify=False)
            if response.status_code == 200:
                users = response.json().get('users', [])
                win = tk.Toplevel()
                win.title("Liste des utilisateurs")
                win.geometry("400x300")
                listbox = tk.Listbox(win, font=("Arial", 12))
                for user in users:
                    listbox.insert(tk.END, f"ID: {user['id']} | Email: {user['email']} | Admin: {user['is_admin']}")
                listbox.pack(fill='both', expand=True, padx=10, pady=10)
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
