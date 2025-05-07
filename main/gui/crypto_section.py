import tkinter as tk
from tkinter import ttk, filedialog
from core import crypto

def create_crypto_section(parent, button_size):
    # Label and divider
    label = tk.Label(parent, text="Cryptographie", font=(None, 14))
    label.grid(row=3, column=0, sticky="w", pady=(30, 5))
    hr = ttk.Separator(parent, orient='horizontal')
    hr.grid(row=4, column=0, sticky='ew', pady=(0, 10))

    # Container for buttons
    frame = ttk.Frame(parent)
    frame.grid(row=5, column=0, sticky='w')

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

    def handle_encrypt():
        filepath = filedialog.askopenfilename()
        if filepath:
            crypto.encrypt_file(filepath)

    def handle_decrypt():
        filepath = filedialog.askopenfilename()
        if filepath:
            crypto.decrypt_file(filepath)

    enc_btn = make_btn(frame, "Encrypt", "🔒", handle_encrypt)
    enc_btn.grid(row=0, column=0, padx=(0, 10))
    dec_btn = make_btn(frame, "Decrypt", "🔓", handle_decrypt)
    dec_btn.grid(row=0, column=1)
