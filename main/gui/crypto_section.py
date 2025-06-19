import tkinter as tk
from tkinter import ttk, filedialog
from core import crypto
import os
from PIL import Image, ImageTk

def create_crypto_section(parent, button_size):
    # Label and divider
    label = tk.Label(parent, text="Cryptographie", font=("Arial", 14))
    label.grid(row=3, column=0, sticky="w", pady=(30, 5))
    hr = ttk.Separator(parent, orient='horizontal')
    hr.grid(row=4, column=0, sticky='ew', pady=(0, 10))

    # Container for buttons
    frame = ttk.Frame(parent)
    frame.grid(row=5, column=0, sticky='w')

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

    def handle_encrypt():
        filepath = filedialog.askopenfilename()
        if filepath:
            crypto.encrypt_file(filepath)

    def handle_decrypt():
        filepath = filedialog.askopenfilename()
        if filepath:
            crypto.decrypt_file(filepath)

    base_dir = os.path.dirname(__file__)
    enc_btn = make_btn(frame, "Chiffré", "🔒", handle_encrypt)
    enc_btn.grid(row=0, column=0, padx=(0, 10))
    dec_btn = make_btn(frame, "Dechiffré", "🔓", handle_decrypt)
    dec_btn.grid(row=0, column=1)
