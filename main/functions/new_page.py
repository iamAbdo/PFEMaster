import tkinter as tk
from tkinter import ttk
from utils.text_formatting import handle_key_press, set_current_page

def add_new_page(app):
    a4_width = int(21/2.54*96)
    a4_height = int(29.7/2.54*96)
    
    page_frame = ttk.Frame(app.container)
    page_frame.pack(pady=20, expand=True)
    
    page_canvas = tk.Canvas(page_frame, width=a4_width, height=a4_height,
                          bg="white", highlightthickness=0)
    page_canvas.pack()
    
    page_canvas.create_rectangle(2, 2, a4_width+2, a4_height+2, fill='#e0e0e0', outline='')
    page_canvas.create_rectangle(0, 0, a4_width, a4_height, fill="white")
    
    text_widget = tk.Text(page_canvas, wrap="word", bg="white", bd=0,
                        font=('Arial', app.root.taille), padx=40, pady=50)
    text_widget.place(x=0, y=0, width=a4_width, height=a4_height)
    
    text_widget.tag_configure("bold", font=('Arial', app.root.taille, 'bold'))
    text_widget.bind("<KeyPress>", lambda e: handle_key_press(app, e))
    text_widget.bind("<FocusIn>", lambda e: set_current_page(app, text_widget))
    
    app.pages.append(text_widget)
    text_widget.focus_set()
    app.current_page = text_widget
