import tkinter as tk
from tkinter import ttk, messagebox
import requests

class CreateUserDialog:
    def __init__(self, parent, jwt_token):
        self.parent = parent
        self.jwt_token = jwt_token
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Créer un nouveau compte")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg="#ffffff")  # Explicit white background
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"400x350+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        main_frame.configure(style="White.TFrame")  # Set style for white background
        
        # Title
        title_label = tk.Label(main_frame, text="Créer un nouveau compte", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Email field
        ttk.Label(form_frame, text="Email:").pack(anchor='w', pady=(0, 5))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(form_frame, textvariable=self.email_var, width=40)
        self.email_entry.pack(fill='x', pady=(0, 15))
        
        # Password field
        ttk.Label(form_frame, text="Mot de passe:").pack(anchor='w', pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                       show="*", width=40)
        self.password_entry.pack(fill='x', pady=(0, 15))
        
        # Confirm password field
        ttk.Label(form_frame, text="Confirmer le mot de passe:").pack(anchor='w', pady=(0, 5))
        self.confirm_password_var = tk.StringVar()
        self.confirm_password_entry = ttk.Entry(form_frame, textvariable=self.confirm_password_var, 
                                               show="*", width=40)
        self.confirm_password_entry.pack(fill='x', pady=(0, 15))
        
        # Role dropdown
        ttk.Label(form_frame, text="Rôle:").pack(anchor='w', pady=(0, 5))
        self.role_var = tk.StringVar(value="Geologue")
        role_options = ["Geologue", "Geophysicien", "Responsable"]
        self.role_dropdown = ttk.Combobox(form_frame, textvariable=self.role_var, values=role_options, state="readonly", width=37)
        self.role_dropdown.pack(fill='x', pady=(0, 15))
        
        # Admin checkbox
        self.is_admin_var = tk.BooleanVar()
        admin_check = ttk.Checkbutton(form_frame, text="Accorder les privilèges d'administrateur", 
                                     variable=self.is_admin_var)
        admin_check.pack(anchor='w', pady=(0, 20))
        
        # Password requirements label
        requirements_text = """Exigences du mot de passe:
• Au moins 8 caractères
• Au moins une majuscule
• Au moins une minuscule
• Au moins un chiffre"""
        
        requirements_label = tk.Label(form_frame, text=requirements_text, 
                                    font=("Arial", 9), fg="gray", justify='left')
        requirements_label.pack(anchor='w', pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="Annuler", command=self.cancel)
        cancel_btn.pack(side='left', padx=(0, 10))
        
        # Green Confirm button (styled like Bootstrap)
        confirm_btn = tk.Button(
            button_frame,
            text="Confirmer",
            command=self.create_user,
            bg="#4CAF50",
            fg="white",
            borderwidth=0,
            padx=10,
            pady=5
        )
        confirm_btn.pack(side='right')
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.config(bg="#45a049"))
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.config(bg="#4CAF50"))
        
        # Bind Enter key to create user
        self.dialog.bind('<Return>', lambda e: self.create_user())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Focus on email entry
        self.email_entry.focus()
        
    def validate_form(self):
        email = self.email_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not email:
            messagebox.showerror("Erreur", "L'email est requis")
            return False
            
        if not password:
            messagebox.showerror("Erreur", "Le mot de passe est requis")
            return False
            
        if password != confirm_password:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
            return False
            
        if len(password) < 8:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 8 caractères")
            return False
            
        return True
        
    def create_user(self):
        if not self.validate_form():
            return
            
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            if self.jwt_token:
                headers['Authorization'] = f'Bearer {self.jwt_token}'
                
            data = {
                'email': self.email_var.get().strip(),
                'password': self.password_var.get(),
                'is_admin': self.is_admin_var.get(),
                'role': self.role_var.get()
            }
            
            response = requests.post(
                'https://127.0.0.1:5000/api/user-management/create-user',
                json=data,
                headers=headers,
                verify=False
            )
            
            if response.status_code == 201:
                messagebox.showinfo("Succès", "Utilisateur créé avec succès!")
                self.result = response.json()
                self.dialog.destroy()
            else:
                error_data = response.json()
                error_message = error_data.get('error', 'Erreur inconnue')
                messagebox.showerror("Erreur", error_message)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de contacter le backend: {e}")
            print(e)
            
    def cancel(self):
        self.dialog.destroy()
        
    def show(self):
        self.dialog.wait_window()
        return self.result

def show_create_user_dialog(parent, jwt_token):
    """Helper function to show the create user dialog"""
    dialog = CreateUserDialog(parent, jwt_token)
    return dialog.show() 