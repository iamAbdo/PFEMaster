import tkinter as tk
from tkinter import ttk

def insert_table(app):
    if not app.current_page:
        return

    dialog = tk.Toplevel(app.root)
    dialog.title("Insert Table")
    dialog.transient(app.root)
    dialog.grab_set()

    rows_var = tk.IntVar(value=2)
    cols_var = tk.IntVar(value=2)

    ttk.Label(dialog, text="Rows:").grid(row=0, column=0, padx=5, pady=5)
    ttk.Spinbox(dialog, from_=1, to=20, textvariable=rows_var).grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(dialog, text="Columns:").grid(row=1, column=0, padx=5, pady=5)
    ttk.Spinbox(dialog, from_=1, to=20, textvariable=cols_var).grid(row=1, column=1, padx=5, pady=5)

    def on_ok():
        rows = rows_var.get()
        cols = cols_var.get()
        dialog.destroy()
        app.current_page.focus_set()
        create_table(app, rows, cols)

    ttk.Button(dialog, text="OK", command=on_ok).grid(row=2, column=0, columnspan=2, pady=5)

def create_table(app, rows, cols):
    text_widget = app.current_page
    table_frame = ttk.Frame(text_widget)
    entries = []
    
    for i in range(rows):
        row_entries = []
        for j in range(cols):
            entry = ttk.Entry(table_frame, width=10)
            entry.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
            row_entries.append(entry)
        entries.append(row_entries)
        table_frame.rowconfigure(i, weight=1)
    
    for j in range(cols):
        table_frame.columnconfigure(j, weight=1)
    
    table_frame.table_entries = entries
    text_widget.window_create("insert", window=table_frame)
