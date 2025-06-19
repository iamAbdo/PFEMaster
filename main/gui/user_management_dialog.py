import tkinter as tk
from tkinter import messagebox
import requests

class CreateUserDialog:
    def __init__(self, parent, jwt_token):
        self.parent = parent
        self.jwt_token = jwt_token
        self.result = None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Créer un nouveau compte")
        width, height = 400, 400
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg="#ffffff")  # Explicit white background

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Container for scrollable content and buttons
        container = tk.Frame(self.dialog, bg="#ffffff")
        container.pack(fill='both', expand=True)

        # Scrollable canvas for form fields
        canvas = tk.Canvas(container, bg="#ffffff", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        self.form_frame = tk.Frame(canvas, bg="#ffffff")
        self.form_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        # Center form_frame in canvas
        canvas.create_window((width // 2, 0), window=self.form_frame, anchor='n')

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Build form inside scrollable frame
        self.create_widgets()

        # Buttons frame fixed at bottom
        button_frame = tk.Frame(self.dialog, bg="#ffffff")
        button_frame.pack(side='bottom', fill='x', padx=20, pady=10)

        # Confirmer button (styled)
        confirmer_btn = tk.Button(
            button_frame,
            text="Confirmer",
            command=self.create_user,
            bg="#4CAF50",
            fg="white",
            borderwidth=0,
            padx=10,
            pady=5
        )
        confirmer_btn.pack(side='left', fill='x', expand=True, padx=(0, 10))
        confirmer_btn.bind("<Enter>", lambda e: confirmer_btn.config(bg="#45a049"))
        confirmer_btn.bind("<Leave>", lambda e: confirmer_btn.config(bg="#4CAF50"))

        # Annuler button
        cancel_btn = tk.Button(button_frame, text="Annuler", command=self.cancel, padx=10, pady=5)
        cancel_btn.pack(side='left', fill='x', expand=True)

        # Remove Enter key binding to prevent form submission on Enter
        self.dialog.unbind('<Return>')
        self.form_entries[0].focus()

    def create_widgets(self):
        # Store for focusing
        self.form_entries = []

        # Title
        title_label = tk.Label(
            self.form_frame,
            text="Créer un nouveau compte",
            font=("Arial", 16, "bold"),
            bg="#ffffff"
        )
        title_label.pack(pady=(20, 20))

        # Email field
        tk.Label(self.form_frame, text="Email:", bg="#ffffff").pack(anchor='center', pady=(0, 5))
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(self.form_frame, textvariable=self.email_var, width=40)
        email_entry.pack(pady=(0, 15))
        self.form_entries.append(email_entry)

        # Password field
        tk.Label(self.form_frame, text="Mot de passe:", bg="#ffffff").pack(anchor='center', pady=(0, 5))
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(self.form_frame, textvariable=self.password_var, show="*", width=40)
        password_entry.pack(pady=(0, 15))
        self.form_entries.append(password_entry)

        # Confirm password field
        tk.Label(self.form_frame, text="Confirmer le mot de passe:", bg="#ffffff").pack(anchor='center', pady=(0, 5))
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.confirm_password_var,
            show="*",
            width=40
        )
        confirm_password_entry.pack(pady=(0, 15))
        self.form_entries.append(confirm_password_entry)

        # Role dropdown
        tk.Label(self.form_frame, text="Rôle:", bg="#ffffff").pack(anchor='center', pady=(0, 5))
        self.role_var = tk.StringVar(value="Geologue")
        role_options = ["Geologue", "Geophysicien", "Responsable"]
        role_menu = tk.OptionMenu(self.form_frame, self.role_var, *role_options)
        role_menu.config(width=37, bg="white", anchor='w')
        role_menu["menu"].config(bg="white")
        role_menu.pack(pady=(0, 15))
        self.form_entries.append(role_menu)

        # Password requirements
        requirements_text = (
            "Exigences du mot de passe:\n"
            "• Au moins 8 caractères\n"
            "• Au moins une majuscule\n"
            "• Au moins une minuscule\n"
            "• Au moins un chiffre"
        )
        requirements_label = tk.Label(
            self.form_frame,
            text=requirements_text,
            font=("Arial", 9),
            fg="gray",
            justify='left',
            bg="#ffffff"
        )
        requirements_label.pack(anchor='center', pady=(0, 10))

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
            headers = {'Content-Type': 'application/json'}
            if self.jwt_token:
                headers['Authorization'] = f'Bearer {self.jwt_token}'

            data = {
                'email': self.email_var.get().strip(),
                'password': self.password_var.get(),
                'role': self.role_var.get(),
                'is_admin': self.role_var.get() == 'Responsable'
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
    return CreateUserDialog(parent, jwt_token).show()
