from tkinter import ttk

def setup_styles():
    style = ttk.Style()
    style.configure('Header.TFrame', background='#f0f0f0')
    style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=6)
    style.map('Bold.TButton',
        background=[('pressed', '#d9d9d9'), ('active', '#ececec')],
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
    )
    style.configure('Bold.TButton', font=('Arial', 10, 'bold'), padding=6)
    style.map('Primary.TButton',
            background=[('active', 'red'), ('!active', 'red')],
            foreground=[('active', 'black'), ('!active', 'black')])
