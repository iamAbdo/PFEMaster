from tkinter import ttk

def setup_styles():
    style = ttk.Style()

    # Header Buttons
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
    
    # Add button
    style.configure('Success.TButton', font=('Arial', 10, 'bold'), padding=6,
                    bg="#4CAF50",
                    fg="white",
                    borderwidth=0,
                    focuscolor=style.configure('.')['background'])
    
    
    style.configure("LogBox.TFrame", padding=0)
    
    # Paper Styling
    style.configure('Column.TFrame', background='#e0e0e0', borderwidth=1, relief='solid', padding=0)
    style.configure('ColumnHeader.TLabel', background='#f0f0f0', relief='ridge', anchor='center')
