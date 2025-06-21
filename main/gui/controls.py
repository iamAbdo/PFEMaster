import tkinter as tk
from tkinter import ttk
from functions.new_page import add_new_page
from utils.text_formatting import toggle_bold
from functions.export_pdf import PDFExporter
from utils.auth_state import get_jwt_token_global

def setup_controls(app):
    control_frame = ttk.Frame(app.header_frame)
    control_frame.pack(pady=10, padx=20, side=tk.LEFT)
    
    ttk.Button(control_frame, text="New Page", command=lambda: add_new_page(app), 
               style='Primary.TButton').pack(side=tk.LEFT, padx=5)
    # app.bold_btn = ttk.Button(control_frame, text="Bold", command=lambda: toggle_bold(app), style='Bold.TButton')
    # app.bold_btn.pack(side=tk.LEFT, padx=5)
    

    # Only show Export PDF button if user is logged in (using global token)
    if get_jwt_token_global():
        ttk.Button(control_frame, text="Export PDF", 
                  command=lambda: PDFExporter(app).export(), 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
    
    ttk.Button(control_frame, text="+ Add Log", command=lambda: app.add_log_box(), 
               style='Primary.TButton').pack(side=tk.LEFT, padx=5)
    
    # Add save button only (removed Ouvrir button)
    ttk.Button(control_frame, text="Sauvegarder", command=lambda: app.save_project(), 
               style='Primary.TButton').pack(side=tk.LEFT, padx=5)
    
    # ttk.Button(
    #     control_frame, 
    #     text="+ Add Log", 
    #     command=lambda: app.add_log_box(),
    #     style='Success.TButton'
    # ).pack(side=tk.LEFT, padx=5)


    # spin_var = tk.IntVar(value=12)
    # ttk.Spinbox(control_frame, from_=1, to=64, textvariable=spin_var).pack(side=tk.LEFT)
    # spin_var.trace_add('write', lambda *args: app.EditSize(spin_var.get()))


