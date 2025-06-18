import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import simpledialog, messagebox
import requests
from gui.crypto_section import create_crypto_section
from gui.admin_section import create_admin_section, set_jwt_token

class SplashWindow:
    def __init__(self, master, on_create_callback):
        self.master = master
        self.on_create = on_create_callback
        self.master.state('zoomed')
        self.master.title("Bienvenue")
        self.jwt_token = None
        self.is_admin = False
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=4)
        self.label_font = font.Font(family="TkDefaultFont", size=10)
        self.hover_font = font.Font(family="TkDefaultFont", size=10, underline=1)
        left = ttk.Frame(master, padding=(10,10,0,10))
        left.grid(row=0, column=0, sticky='nsew')
        content = ttk.Frame(left)
        content.pack(side='left', fill='both', expand=True)
        from PIL import Image, ImageTk
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "..", "images", "Sonatrach.png")
        logo_path = os.path.normpath(logo_path)
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_container = ttk.Frame(content)
            logo_container.pack(anchor='nw', pady=(0, 20))
            logo_label = tk.Label(logo_container, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.pack(anchor='w')
            logo_text = tk.Label(logo_container, text="Sonatrach", font=("Arial", 12, "bold"))
            logo_text.pack(anchor='w')
        else:
            print(f"Image non trouvée à : {logo_path}")
        left_menu_items = [
            "Paramètres",
            "Compte",
            "Aide",
            "À propos",
            "Support",
            "Historique"
        ]
        for text in left_menu_items:
            lbl = tk.Label(
                content,
                text=text,
                cursor='hand2',
                font=self.label_font,
                width=15,
                anchor='w'
            )
            lbl.pack(anchor='nw', pady=5)
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(font=self.hover_font, fg="blue"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(font=self.label_font, fg="black"))
            if text == "Compte":
                lbl.bind("<Button-1>", lambda e: self._on_account_click())
            elif text == "À propos":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("À propos", "Sincus Fiche carottes\nENAGEO - Sonatrach © 2025"))
            elif text == "Aide":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Aide", "Consultez la documentation ou contactez le support."))
            elif text == "Support":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Support", "Email : support@sonatrach.dz"))
            else:
                lbl.bind("<Button-1>", lambda e: None)
        right = ttk.Frame(master, padding=(20,10,10,10))
        right.grid(row=0, column=1, sticky='nsew')
        right.columnconfigure(0, weight=1)
        desc = tk.Label(right, text="Gestion de Projet", font=(None, 14))
        desc.grid(row=0, column=0, pady=(0,5), sticky='w')
        hr = ttk.Separator(right, orient='horizontal')
        hr.grid(row=1, column=0, sticky='ew', pady=(0,10))
        self.master.update_idletasks()
        screen_h = self.master.winfo_screenheight()
        square = int(screen_h * 0.35)
        button_frame = ttk.Frame(right)
        button_frame.grid(row=2, column=0, sticky='w')
        create_btn = tk.Frame(
            button_frame,
            width=square,
            height=square,
            relief='raised',
            borderwidth=2,
            cursor='hand2'
        )
        create_btn.grid(row=0, column=0, sticky='w', padx=(0,10))
        create_btn.grid_propagate(False)
        plus = tk.Label(create_btn, text="+", font=("Arial", 48), fg="gray")
        plus.pack(expand=True)
        txt = tk.Label(create_btn, text="Créer un nouveau projet")
        txt.pack(side='bottom', pady=10)
        for widget in (create_btn, plus, txt):
            widget.bind("<Button-1>", lambda e: self._create())
        open_btn = tk.Frame(
            button_frame,
            width=square,
            height=square,
            relief='raised',
            borderwidth=2,
            cursor='hand2'
        )
        open_btn.grid(row=0, column=1, sticky='w')
        open_btn.grid_propagate(False)
        folder = tk.Label(open_btn, text="📁", font=("Arial", 48), fg="gray")
        folder.pack(expand=True)
        txt2 = tk.Label(open_btn, text="Ouvrir un projet existant")
        txt2.pack(side='bottom', pady=10)
        for widget in (open_btn, folder, txt2):
            widget.bind("<Button-1>", lambda e: None)
        create_crypto_section(right, square)
        create_admin_section(right, square, self.jwt_token)

    def _create(self):
        self.master.state('normal')
        for widget in self.master.winfo_children():
            widget.destroy()
        for i in range(self.master.grid_size()[0]):
            self.master.columnconfigure(i, weight=0)
        for i in range(self.master.grid_size()[1]):
            self.master.rowconfigure(i, weight=0)
        self.on_create()

    def _on_account_click(self):
        if self.jwt_token:
            response = messagebox.askquestion(
                "Déconnexion",
                f"Vous êtes connecté.\n\nVoulez-vous vous déconnecter ?",
                icon='question'
            )
            if response == 'yes':
                self.jwt_token = None
                self.is_admin = False
                set_jwt_token(None)
                messagebox.showinfo("Déconnexion", "Vous avez été déconnecté.")
        else:
            email = simpledialog.askstring("Connexion", "Entrez l'email :")
            if not email:
                return
            password = simpledialog.askstring("Connexion", "Entrez le mot de passe :", show="*")
            if not password or len(password) < 8:
                messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 8 caractères.")
                return
            try:
                response = requests.post(
                    'https://127.0.0.1:5000/api/auth/login',
                    json={"email": email, "password": password},
                    verify=False  # For dev only; use CA in prod
                )
                if response.status_code == 200:
                    data = response.json()
                    self.jwt_token = data['token']
                    self.is_admin = data.get('is_admin', False)
                    set_jwt_token(self.jwt_token)
                    messagebox.showinfo("Connecté", f"Connecté en tant que {email}.")
                else:
                    messagebox.showerror("Erreur", f"Erreur de connexion : {response.text}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la connexion : {e}")
