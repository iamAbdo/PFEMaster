import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys
from pathlib import Path
from core import account as acc

class LoginWindow:
    def __init__(self, master, on_login_success):
        self.master = master
        self.on_login_success = on_login_success
        self.master.title("PFEMaster - Login")
        self.master.state('zoomed')
        
        # Configure grid layout (1:2 ratio)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=2)
        self.master.rowconfigure(0, weight=1)

        # Left side - Logo panel
        self.left_frame = ttk.Frame(self.master)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        
        # Right side - Login form
        self.right_frame = ttk.Frame(self.master)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Load and display logo
        self.load_logo()
        
        # Create login form
        self.create_login_form()

    def get_base_path(self):
        """Get the absolute path to the project root"""
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (pyinstaller)
            return Path(sys.executable).parent
        else:
            # Normal execution
            return Path(__file__).parent.parent.parent  # gui -> main -> PFEMaster

    def load_logo(self):
        """Load and display the company logo with proper path resolution"""
        try:
            base_path = self.get_base_path()
            image_path = base_path / "images" / "Sonatrach.png"
            
            if not image_path.exists():
                raise FileNotFoundError(f"Logo not found at: {image_path}")
                
            img = Image.open(image_path)
            img = img.resize((self.get_logo_size(), self.get_logo_size()), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            
            logo_label = ttk.Label(self.left_frame, image=self.logo_img)
            logo_label.pack(expand=True, fill='both')
            
            # Add border around logo
            self.left_frame.config(borderwidth=2, relief='groove')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logo: {str(e)}")
            # Create placeholder if image fails to load
            placeholder = ttk.Label(self.left_frame, text="Company Logo", font=('Arial', 24))
            placeholder.pack(expand=True)

    def get_logo_size(self):
        """Calculate logo size based on screen height"""
        screen_height = self.master.winfo_screenheight()
        return int(screen_height * 0.8)  # 80% of screen height

    def create_login_form(self):
        """Create the login form components"""
        container = ttk.Frame(self.right_frame)
        container.pack(expand=True, padx=100, pady=50)

        # Email Entry
        ttk.Label(container, text="Email:", font=('Arial', 12)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.email_entry = ttk.Entry(container, font=('Arial', 12))
        self.email_entry.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        # Password Entry
        ttk.Label(container, text="Password:", font=('Arial', 12)).grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.password_entry = ttk.Entry(container, show="*", font=('Arial', 12))
        self.password_entry.grid(row=3, column=0, sticky='ew', pady=(0, 30))

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.grid(row=4, column=0, sticky='ew')
        
        ttk.Button(button_frame, text="Close", command=self.master.destroy).pack(side='left', expand=True)
        ttk.Button(button_frame, text="Login", command=self.attempt_login).pack(side='left', expand=True, padx=10)

        # Configure column weights
        container.columnconfigure(0, weight=1)

    def attempt_login(self):
        """Handle login attempt"""
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning("Validation Error", "Please fill in both email and password")
            return

        try:
            # Replace with actual authentication logic
            user_data = acc.save_account(email, password)
            messagebox.showinfo("Login Success", f"Welcome {user_data['username']}")
            self.on_login_success()
        except Exception as e:
            messagebox.showerror("Login Failed", str(e))