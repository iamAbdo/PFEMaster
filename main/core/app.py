import tkinter as tk
from tkinter import ttk
from gui.controls import setup_controls
from gui.canvas import setup_canvas
from utils.styles import setup_styles
from functions.new_page import add_new_page

class WordApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Application")
        self.root.state('zoomed')
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.pages = []
        self.bold_on = False
        self.current_font = ("Arial", 12)
        self.root.taille = 12
        self.current_page = None

        self.status_bar = ttk.Label(self.root, text="Total pages: 0", style='Status.TLabel')
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        self.header_frame = ttk.Frame(self.root, height=80, style='Header.TFrame')
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        
        
        setup_styles()
        setup_controls(self)
        setup_canvas(self)
        add_new_page(self)

        self.configure_tags()

    def EditSize(self, taille):
        self.root.taille = taille
        if self.current_page:
            for text_widget in self.current_page:
                text_widget.configure(font=('Arial', self.root.taille))
                text_widget.tag_configure("bold", font=('Arial', self.root.taille, 'bold'))

    def configure_tags(self):
        # Initialize bold tag for all existing text widgets
        for page in self.pages:
            for text_widget in page:
                text_widget.tag_configure("bold", font=('Arial', self.root.taille, 'bold'))
