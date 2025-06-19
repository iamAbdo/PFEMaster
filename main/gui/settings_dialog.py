import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from pathlib import Path
from utils.settings import get_settings_file

class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.settings_path = get_settings_file()
        self.settings = self.load_settings()
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Paramètres")
        self.dialog.geometry("450x180")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_window()
        self.create_widgets()

    def load_settings(self):
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_settings(self):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            messagebox.showinfo("Succès", "Paramètres enregistrés.")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer les paramètres : {e}")

    def get_default_dir(self):
        # Default to user's Documents folder
        return str(Path.home() / 'Documents')

    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Dossier de sauvegarde par défaut :", font=("Arial", 11)).pack(anchor='w')
        self.dir_var = tk.StringVar()
        current_dir = self.settings.get('save_dir', self.get_default_dir())
        self.dir_var.set(current_dir)
        self.dir_label = ttk.Label(frame, textvariable=self.dir_var, relief='sunken', anchor='w', width=50)
        self.dir_label.pack(fill='x', pady=(5, 10))

        choose_btn = ttk.Button(frame, text="Choisir...", command=self.choose_directory)
        choose_btn.pack(anchor='w')

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        save_btn = ttk.Button(btn_frame, text="Enregistrer", command=self.on_save)
        save_btn.pack(side='right', padx=(0, 10))
        cancel_btn = ttk.Button(btn_frame, text="Annuler", command=self.dialog.destroy)
        cancel_btn.pack(side='right')

    def choose_directory(self):
        new_dir = filedialog.askdirectory(parent=self.dialog, title="Choisir un dossier de sauvegarde")
        if new_dir:
            self.dir_var.set(new_dir)

    def on_save(self):
        self.settings['save_dir'] = self.dir_var.get()
        self.save_settings()

    def center_window(self):
        self.dialog.update_idletasks()
        w = self.dialog.winfo_width()
        h = self.dialog.winfo_height()
        ws = self.dialog.winfo_screenwidth()
        hs = self.dialog.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")

    def show(self):
        self.dialog.wait_window()
        return self.result

def show_settings_dialog(parent):
    dialog = SettingsDialog(parent)
    return dialog.show() 