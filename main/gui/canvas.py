import tkinter as tk
from tkinter import ttk
from utils.events import on_canvas_configure, on_frame_configure

def setup_canvas(app):
    app.canvas = tk.Canvas(app.content_frame, bg='#f5f5f5', highlightthickness=0)
    app.v_scroll = ttk.Scrollbar(app.content_frame, orient="vertical", command=app.canvas.yview)
    app.canvas.configure(yscrollcommand=app.v_scroll.set)
    
    app.canvas.grid(row=0, column=0, sticky="nsew")
    app.v_scroll.grid(row=0, column=1, sticky="ns")
    
    app.content_frame.grid_rowconfigure(0, weight=1)
    app.content_frame.grid_columnconfigure(0, weight=1)
    
    app.container = ttk.Frame(app.canvas)
    app.canvas.create_window((app.canvas.winfo_width()//2, 20), 
                           window=app.container, anchor="n", tags="container")
    
    app.canvas.bind("<Configure>", lambda e: on_canvas_configure(app, e))
    app.container.bind("<Configure>", lambda e: on_frame_configure(app, e))
