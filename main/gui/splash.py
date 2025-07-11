import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font
from tkinter import simpledialog
import requests
import json
from gui.crypto_section import create_crypto_section
from gui.admin_section import create_admin_section, set_jwt_token
from PIL import Image, ImageTk
import os
from gui.settings_dialog import show_settings_dialog
from gui.history_dialog import show_history_dialog
from core.app import Sincus
from utils.auth_state import get_jwt_token_global, set_jwt_token_global

class SplashWindow:
    def __init__(self, master, on_create_callback):
        self.master = master
        self.on_create = on_create_callback
        self.master.state('zoomed')
        self.master.title("Bienvenue")
        self.jwt_token = None
        self.is_admin = False
        self.role = None
        self.left_menu_labels = {}
        # Add header row
        self.master.rowconfigure(0, weight=0)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=4)
        self.label_font = font.Font(family="TkDefaultFont", size=10)
        self.hover_font = font.Font(family="TkDefaultFont", size=10, underline=True)

        # --- HEADER SECTION ---
        header = tk.Frame(master, bg="#f7c97c", height=80)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        header.grid_propagate(False)
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=3)
        header.columnconfigure(2, weight=1)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sonatrach_path = os.path.normpath(os.path.join(current_dir, "..", "images", "Sonatrach.png"))
        enageo_path = os.path.normpath(os.path.join(current_dir, "..", "images", "enageo-logo-text-white.png"))
        # Sonatrach logo (left)
        if os.path.exists(sonatrach_path):
            sonatrach_img = Image.open(sonatrach_path)
            sonatrach_img = sonatrach_img.resize((60, 60), Image.Resampling.LANCZOS)
            sonatrach_photo = ImageTk.PhotoImage(sonatrach_img)
            self.sonatrach_photo = sonatrach_photo
            logo_label = tk.Label(header, image=self.sonatrach_photo, bg="#f7c97c")
            logo_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        # ENAGEO logo (right)
        if os.path.exists(enageo_path):
            enageo_img = Image.open(enageo_path)
            enageo_img = enageo_img.resize((120, 40), Image.Resampling.LANCZOS)
            enageo_photo = ImageTk.PhotoImage(enageo_img)
            enageo_label = tk.Label(header, image=enageo_photo, bg="#f7c97c")
            enageo_label.grid(row=0, column=2, padx=20, pady=10, sticky="e")
            self.enageo_photo = enageo_photo  # Keep reference
        # Centered title
        title_label = tk.Label(header, text="PROGRAM DE GESTION DES FICHES CAROTTES", bg="#f7c97c", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Helper function for rounded rectangle
        def draw_rounded_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
            # Draw corners
            canvas.create_arc(x1, y1, x1+r*2, y1+r*2, start=90, extent=90, style='pieslice', **kwargs)
            canvas.create_arc(x2-r*2, y1, x2, y1+r*2, start=0, extent=90, style='pieslice', **kwargs)
            canvas.create_arc(x2-r*2, y2-r*2, x2, y2, start=270, extent=90, style='pieslice', **kwargs)
            canvas.create_arc(x1, y2-r*2, x1+r*2, y2, start=180, extent=90, style='pieslice', **kwargs)
            # Draw sides and center
            canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
            canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)

        # --- LEFT SECTION ---
        left = ttk.Frame(master, padding=(10,10,0,10))
        left.grid(row=1, column=0, sticky='nsew')
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        content = ttk.Frame(left)
        content.pack(side='left', fill='both', expand=True)
        # Remove logo from left section
        left_menu_items = [
            "Paramètres",
            "Compte",
            "Aide",
            "À propos",
            "Support",
        ]
        
        # Add "Historique" only for admins
        if self.is_admin:
            left_menu_items.append("Historique")
            
        for text in left_menu_items:
            btn_canvas = tk.Canvas(content, width=160, height=36, highlightthickness=0)
            btn_canvas.pack(anchor='nw', pady=7)
            self.draw_rounded_rect(btn_canvas, 2, 2, 158, 34, r=16, fill="#f7c97c", outline="")
            # Dynamic label for Compte/Log in
            label_text = text
            if text == "Compte":
                label_text = "Compte" if self.jwt_token else "Log in"
            lbl = tk.Label(btn_canvas, text=label_text, cursor='hand2', font=self.label_font, bg="#f7c97c", width=13, anchor='w')
            self.left_menu_labels[text] = lbl
            lbl.place(x=16, y=6)
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(font=self.hover_font, fg="blue"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(font=self.label_font, fg="black"))
            if text == "Paramètres":
                lbl.bind("<Button-1>", lambda e: show_settings_dialog(self.master))
            elif text == "Compte":
                lbl.bind("<Button-1>", lambda e: self._on_account_click())
            elif text == "À propos":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("À propos", "Sincus Fiche carottes\nENAGEO - Sonatrach © 2025"))
            elif text == "Aide":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Aide", "Consultez la documentation ou contactez le support."))
            elif text == "Support":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Support", "Email : support@sonatrach.dz"))
            elif text == "Historique":
                lbl.bind("<Button-1>", lambda e: show_history_dialog(self.master))
            else:
                lbl.bind("<Button-1>", lambda e: None)

        # --- RIGHT SECTION ---
        self._refresh_right_section()

    def _refresh_right_section(self):
        # Destroy current right section
        for widget in self.master.grid_slaves(row=1, column=1):
            widget.destroy()
        right_container = ttk.Frame(self.master, padding=(20,10,10,10))
        right_container.grid(row=1, column=1, sticky='nsew')
        right_container.columnconfigure(0, weight=1)

        # --- ALWAYS USE CANVAS+FRAME FOR SCROLLABILITY ---
        canvas = tk.Canvas(right_container, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(right_container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        # Don't grid vscroll yet
        right_container.rowconfigure(0, weight=1)
        right_container.columnconfigure(0, weight=1)

        def resize_scroll_frame(event=None):
            # Make scroll_frame always as wide as the canvas (minus scrollbar)
            canvas_width = canvas.winfo_width()
            canvas.itemconfig(scroll_window, width=canvas_width)
            scroll_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", resize_scroll_frame)
        right_container.bind("<Configure>", lambda e: resize_scroll_frame())

        right = scroll_frame
        right.columnconfigure(0, weight=1)
        # --- PROJECT LINE ---
        desc = tk.Label(right, text="Gestion de Projet", font=("Arial", 14))
        desc.grid(row=0, column=0, pady=(0,2), sticky='w')
        hr = ttk.Separator(right, orient='horizontal')
        hr.grid(row=1, column=0, sticky='ew', pady=(0,4))
        # --- BUTTON SIZE LOGIC ---
        screen_h = self.master.winfo_screenheight()
        btn_height = int(screen_h * 0.18)
        btn_width = int(btn_height * 2.2)
        button_frame = ttk.Frame(right)
        button_frame.grid(row=2, column=0, sticky='w', pady=(0,2))
        def make_rect_btn(parent, text, emoji, command=None):
            btn = tk.Frame(parent, width=btn_width, height=btn_height, bg="#f7c97c", relief='raised', borderwidth=2, cursor='hand2')
            btn.grid_propagate(False)
            icon_label = tk.Label(btn, text=emoji, font=("Arial", int(btn_height*0.4)), fg="gray", bg="#f7c97c")
            icon_label.pack(expand=True)
            txt_label = tk.Label(btn, text=text, bg="#f7c97c")
            txt_label.pack(side='bottom', pady=10)
            widgets = [btn, icon_label, txt_label]
            if command:
                for w in widgets:
                    w.bind("<Button-1>", lambda e: command())
            return btn
        create_btn = make_rect_btn(button_frame, "Créer un nouveau projet", "➕", self._create)
        create_btn.grid(row=0, column=0, sticky='w', padx=(0,10))
        open_btn = make_rect_btn(button_frame, "Ouvrir un projet existant", "📁", self._open)
        open_btn.grid(row=0, column=1, sticky='w')
        # --- CRYPTO SECTION ---
        if self.jwt_token:
            create_crypto_section(right, btn_height)  # crypto section already uses reduced padding
            # --- GESTION SECTION ---
            if self.role in ("Geophysicien", "Responsable"):
                create_admin_section(right, btn_height, self.jwt_token, self.role)  # gestion section already uses reduced padding

        # --- SCROLLBAR LOGIC: Only show if needed ---
        def update_scrollbar():
            scroll_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            if scroll_frame.winfo_height() > right_container.winfo_height():
                vscroll.grid(row=0, column=1, sticky="ns")
            else:
                vscroll.grid_forget()
        right_container.after(100, update_scrollbar)
        # Also update scrollbar on resize
        canvas.bind("<Configure>", lambda e: update_scrollbar())
        right_container.bind("<Configure>", lambda e: update_scrollbar())

    def _create(self):
        self.master.state('normal')
        for widget in self.master.winfo_children():
            widget.destroy()
        for i in range(self.master.grid_size()[0]):
            self.master.columnconfigure(i, weight=0)
        for i in range(self.master.grid_size()[1]):
            self.master.rowconfigure(i, weight=0)
        self.on_create(self.jwt_token)

    def _open(self):
        """Open an existing .sincus project file"""
        print("=== Starting _open in splash screen ===")
        file_path = filedialog.askopenfilename(
            filetypes=[("Sincus Files", "*.sincus"), ("All Files", "*.*")],
            title="Ouvrir un projet existant"
        )
        
        if not file_path:
            print("No file selected, aborting")
            return
            
        print(f"Selected file: {file_path}")
        
        try:
            print("Reading file...")
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            print("File read successfully")
            
            # Extract project info from the saved file
            project_info = save_data.get('project_info', {})
            print(f"Project info extracted: {list(project_info.keys())}")
            
            # Clear the splash screen and start the main app
            print("Clearing splash screen...")
            self.master.state('normal')
            
            print("Destroying splash widgets...")
            for widget in self.master.winfo_children():
                try:
                    widget.destroy()
                    print("  Widget destroyed successfully")
                except Exception as e:
                    print(f"  WARNING: Could not destroy widget: {e}")
            
            print("Resetting grid configuration...")
            for i in range(self.master.grid_size()[0]):
                self.master.columnconfigure(i, weight=0)
            for i in range(self.master.grid_size()[1]):
                self.master.rowconfigure(i, weight=0)
            
            print("Creating Sincus app...")
            # Start main application with loaded project info and global JWT token
            app = Sincus(self.master, project_info, get_jwt_token_global())
            print("Sincus app created successfully")
            
            # Load the saved data into the app after ensuring it's initialized
            def load_when_ready():
                print("=== load_when_ready called ===")
                try:
                    if app.is_initialized():
                        print("App is initialized, loading project data...")
                        app.load_project_data(save_data)
                    else:
                        print("App not yet initialized, retrying...")
                        # Retry after a longer delay
                        self.master.after(200, load_when_ready)
                except Exception as e:
                    print(f"ERROR in load_when_ready: {e}")
                    import traceback
                    traceback.print_exc()
                    messagebox.showerror("Erreur", f"Erreur lors de l'initialisation :\n{str(e)}")
            
            print("Scheduling load_when_ready...")
            self.master.after(1000, load_when_ready)  # Increased delay to 1 second
            print("load_when_ready scheduled")
            
        except Exception as e:
            print(f"ERROR in _open: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture du fichier :\n{str(e)}")

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
                self.role = None
                set_jwt_token(None)
                # Also clear the global token
                set_jwt_token_global(None)
                if "Compte" in self.left_menu_labels:
                    self.left_menu_labels["Compte"].config(text="Log in")
                messagebox.showinfo("Déconnexion", "Vous avez été déconnecté.")
                self._refresh_entire_interface()
        else:
            # Création d'une fenêtre modale pour saisir email et mot de passe simultanément
            login_win = tk.Toplevel(self.master)
            login_win.title("Connexion")
            login_win.transient(self.master)
            login_win.grab_set()
            login_win.resizable(False, False)
            
            # Configure grid weights for better layout
            login_win.columnconfigure(1, weight=1)
            
            email_var = tk.StringVar()
            pwd_var = tk.StringVar()
            
            # Title label
            title_label = tk.Label(login_win, text="Connexion à l'application", font=("Arial", 12, "bold"))
            title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15), sticky='ew')
            
            # Email section with better label
            email_label = tk.Label(login_win, text="Adresse email :", font=("Arial", 10), anchor='w')
            email_label.grid(row=1, column=0, padx=(20, 10), pady=(0, 5), sticky='w')
            email_entry = tk.Entry(login_win, textvariable=email_var, width=30, font=("Arial", 10))
            email_entry.grid(row=1, column=1, padx=(0, 20), pady=(0, 5), sticky='ew')
            
            # Password section with better label
            pwd_label = tk.Label(login_win, text="Mot de passe :", font=("Arial", 10), anchor='w')
            pwd_label.grid(row=2, column=0, padx=(20, 10), pady=(0, 5), sticky='w')
            pwd_entry = tk.Entry(login_win, textvariable=pwd_var, show="*", width=30, font=("Arial", 10))
            pwd_entry.grid(row=2, column=1, padx=(0, 20), pady=(0, 5), sticky='ew')
            
            # Button frame
            btn_frame = tk.Frame(login_win)
            btn_frame.grid(row=3, column=0, columnspan=2, pady=(15, 20))
            
            def on_ok():
                login_win.destroy()
                
            def on_cancel():
                email_var.set('')
                pwd_var.set('')
                login_win.destroy()
                
            def on_enter(event):
                on_ok()
            
            # Colored buttons
            ok_btn = tk.Button(btn_frame, text="Se connecter", width=12, command=on_ok, 
                              bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                              relief="flat", padx=15, pady=5)
            ok_btn.pack(side='left', padx=5)
            
            cancel_btn = tk.Button(btn_frame, text="Annuler", width=12, command=on_cancel,
                                  bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                                  relief="flat", padx=15, pady=5)
            cancel_btn.pack(side='left', padx=5)
            
            # Bind Enter key to confirm
            email_entry.bind("<Return>", on_enter)
            pwd_entry.bind("<Return>", on_enter)
            
            # Center the window
            login_win.update_idletasks()
            win_w = login_win.winfo_width()
            win_h = login_win.winfo_height()
            screen_w = login_win.winfo_screenwidth()
            screen_h = login_win.winfo_screenheight()
            x = (screen_w // 2) - (win_w // 2)
            y = (screen_h // 2) - (win_h // 2)
            login_win.geometry(f"{win_w}x{win_h}+{x}+{y}")
            
            # Set focus to email entry
            email_entry.focus_set()
            
            # Wait for window to close
            self.master.wait_window(login_win)
            email = email_var.get().strip()
            password = pwd_var.get()
            if not email or not password:
                return
            if len(password) < 8:
                messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 8 caractères.")
                return
            try:
                response = requests.post(
                    'https://127.0.0.1:5000/api/auth/login',
                    json={"email": email, "password": password},
                    verify=False
                )
                if response.status_code == 200:
                    data = response.json()
                    self.jwt_token = data['token']
                    self.is_admin = data.get('is_admin', False)
                    self.role = data.get('role', None)
                    set_jwt_token(self.jwt_token)
                    # Also set the global token for use across the application
                    set_jwt_token_global(self.jwt_token)
                    if "Compte" in self.left_menu_labels:
                        self.left_menu_labels["Compte"].config(text="Compte")
                    messagebox.showinfo("Connecté", f"Connecté en tant que {email}.")
                    self._refresh_entire_interface()
                else:
                    messagebox.showerror("Erreur", f"Erreur de connexion : {response.text}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la connexion : {e}")

    def _refresh_entire_interface(self):
        """Refresh both left menu and right section when admin status changes"""
        # Destroy current left section
        for widget in self.master.grid_slaves(row=1, column=0):
            widget.destroy()
        
        # Recreate left section
        left = ttk.Frame(self.master, padding=(10,10,0,10))
        left.grid(row=1, column=0, sticky='nsew')
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)
        content = ttk.Frame(left)
        content.pack(side='left', fill='both', expand=True)
        
        # Clear the labels dictionary
        self.left_menu_labels = {}
        
        # Recreate left menu items
        left_menu_items = [
            "Paramètres",
            "Compte",
            "Aide",
            "À propos",
            "Support",
        ]
        
        # Add "Historique" only for admins
        if self.is_admin:
            left_menu_items.append("Historique")
            
        for text in left_menu_items:
            btn_canvas = tk.Canvas(content, width=160, height=36, highlightthickness=0)
            btn_canvas.pack(anchor='nw', pady=7)
            self.draw_rounded_rect(btn_canvas, 2, 2, 158, 34, r=16, fill="#f7c97c", outline="")
            # Dynamic label for Compte/Log in
            label_text = text
            if text == "Compte":
                label_text = "Compte" if self.jwt_token else "Log in"
            lbl = tk.Label(btn_canvas, text=label_text, cursor='hand2', font=self.label_font, bg="#f7c97c", width=13, anchor='w')
            self.left_menu_labels[text] = lbl
            lbl.place(x=16, y=6)
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(font=self.hover_font, fg="blue"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(font=self.label_font, fg="black"))
            if text == "Paramètres":
                lbl.bind("<Button-1>", lambda e: show_settings_dialog(self.master))
            elif text == "Compte":
                lbl.bind("<Button-1>", lambda e: self._on_account_click())
            elif text == "À propos":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("À propos", "Sincus Fiche carottes\nENAGEO - Sonatrach © 2025"))
            elif text == "Aide":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Aide", "Consultez la documentation ou contactez le support."))
            elif text == "Support":
                lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Support", "Email : support@sonatrach.dz"))
            elif text == "Historique":
                lbl.bind("<Button-1>", lambda e: show_history_dialog(self.master))
            else:
                lbl.bind("<Button-1>", lambda e: None)
        
        # Refresh right section
        self._refresh_right_section()

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, r=16, **kwargs):
        # Draw corners
        canvas.create_arc(x1, y1, x1+r*2, y1+r*2, start=90, extent=90, style='pieslice', **kwargs)
        canvas.create_arc(x2-r*2, y1, x2, y1+r*2, start=0, extent=90, style='pieslice', **kwargs)
        canvas.create_arc(x2-r*2, y2-r*2, x2, y2, start=270, extent=90, style='pieslice', **kwargs)
        canvas.create_arc(x1, y2-r*2, x1+r*2, y2, start=180, extent=90, style='pieslice', **kwargs)
        # Draw sides and center
        canvas.create_rectangle(x1+r, y1, x2-r, y2, **kwargs)
        canvas.create_rectangle(x1, y1+r, x2, y2-r, **kwargs)
