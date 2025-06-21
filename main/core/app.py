import tkinter as tk
import re
import json
import pickle
from tkinter import ttk, colorchooser, filedialog, messagebox
from gui.controls import setup_controls
from gui.canvas import setup_canvas
from utils.styles import setup_styles
from functions.new_page import add_new_page
from reportlab.lib.pagesizes import A4
from utils.auth_state import get_jwt_token_global

class Sincus:
    def __init__(self, root, project_info, jwt_token=None):
        a4_width, a4_height = A4
    
        self.a4_width = int(a4_width)
        self.a4_height = int(a4_height)
        
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
        
        # Store JWT token (use global if not provided)
        self.jwt_token = jwt_token or get_jwt_token_global()

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Total pages: 0", style='Status.TLabel')
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        # Header Frame
        self.header_frame = ttk.Frame(self.root, height=80, style='Header.TFrame')
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        
        # Toggle Button
        self.toggle_info_btn = ttk.Button(
            self.header_frame, 
            text="Show Project Info", 
            command=self.toggle_project_info
        )
        self.toggle_info_btn.pack(side="right", padx=10, pady=10)

        # Project Info Container (initially hidden)
        self.project_info_container = ttk.Frame(self.root)
    
        # Content Frame (starts in row 1)
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew")

        # Grid configuration
        self.root.grid_rowconfigure(0, weight=0)  # Header
        self.root.grid_rowconfigure(1, weight=1)  # Content
        self.root.grid_rowconfigure(2, weight=0)  # Project Info
        self.root.grid_columnconfigure(0, weight=1)
        # Content Frame (always in row 1)
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew")


        # Project Information
        self.project_info = project_info
        self.TeteStart = int(re.sub(r'[^\d]', '', self.project_info['tete']))

        # Tracking boxes
        self.log_boxes = []  
        self.current_expandable = None
        
        # Add missing attributes to fix linter errors
        self._log_min_height = 50
        self._log_max_height = 200
        self.container = None  # Will be set by setup_canvas
        self.texture_labels = {}  # Track texture labels
        
        # Setup components
        setup_styles()
        setup_controls(self)
        setup_canvas(self)
        add_new_page(self)
        self.configure_tags()
        
        # Add keyboard shortcut for return to splash
        self.root.bind("<Control-Home>", lambda e: self.return_to_splash())

    def create_project_info_table(self):
        # 1) Clear existing widgets
        for w in self.project_info_container.winfo_children():
            w.destroy()

        # 2) Fix the outer container to A4 width, disable propagation
        self.project_info_container.config(
            width=self.a4_width,
            height=200
        )
        self.project_info_container.pack_propagate(False)
        self.project_info_container.grid_propagate(False)

        # 3) Create & fix the inner table frame with solid border
        table_frame = ttk.Frame(self.project_info_container, borderwidth=1, relief='solid')
        table_frame.config(width=self.a4_width)
        table_frame.pack(expand=True, fill='both')
        table_frame.pack_propagate(False)
        table_frame.grid_propagate(False)

        # 4) Define your cells: (text, row, column, rowspan, colspan)
        cells = [
            # Rows 1–4
            ("EXPLORATION‐PRODUCTION\nDivision\nExploration\nDirection des Operations\nExploration\nDpt: Géologie\nHASSI ‐ MESSAOUD",
            0, 0, 4, 6),
            (self.project_info.get('carotte_summary', ''), 0, 6, 4, 4),
            ("Puits :", 0, 10, 1, 1),
            (self.project_info.get('puits', ''), 0, 11, 1, 1),
            ("Sigle :", 1, 10, 1, 1),
            (self.project_info.get('sigle', ''), 1, 11, 1, 1),
            ("Permis :", 2, 10, 1, 1),
            (self.project_info.get('permis', ''), 2, 11, 1, 1),
            ("Bloc :", 3, 10, 1, 1),
            (self.project_info.get('bloc', ''), 3, 11, 1, 1),

            # Rows 5–7
            (f"Echelle : {self.project_info.get('echelle', '')}", 4, 0, 3, 6),
            (f"Carottier: {self.project_info.get('carottier', '')}", 4, 6, 1, 3),
            (f"Type de Boue : {self.project_info.get('mud_type', '')}", 4, 9, 1, 2),
            (f"Carrote: {self.project_info.get('carotte', '')}", 4, 11, 1, 1),
            (f"Couronne: {self.project_info.get('couronne', '')}", 5, 6, 1, 3),
            (f"D : {self.project_info.get('d_value', '')}", 5, 9, 1, 1),
            ("Tete:", 5, 10, 1, 1),
            (self.project_info.get('tete', ''), 5, 11, 1, 1),
            (f"Type: {self.project_info.get('core_type', '')}", 6, 6, 1, 3),
            (f"FUN VIS (s/qt) : {self.project_info.get('fun_vis', '')}", 6, 9, 1, 1),
            ("Pied:", 6, 10, 1, 1),
            (self.project_info.get('pied', ''), 6, 11, 1, 1),

            # Rows 8–9
            ("Côtes (m)", 7, 0, 2, 1),
            ("Log", 7, 1, 2, 1),
            ("Nº", 7, 2, 1, 1),
            ("INDICES", 7, 3, 1, 2),
            ("Fissures", 7, 5, 2, 1),
            ("Pendage", 7, 6, 2, 1),
            ("Calcimètrie", 7, 7, 1, 1),
            ("Age", 7, 8, 1, 1),
            ("D E S C R I P T I O N  L I T H O L O G I Q U E  &  O B S E R V A T I O N S",
            7, 9, 2, 3),
            ("Echan", 8, 2, 1, 1),
            ("direct", 8, 3, 1, 1),
            ("Indir", 8, 4, 1, 1),
            ("25", 8, 7, 1, 1),
            ("75", 8, 8, 1, 1),
        ]

        # 5) Create each label and grid it with single border
        for text, r, c, rs, cs in cells:
            lbl = ttk.Label(table_frame,
                            text=text,
                            relief='solid',
                            borderwidth=1,
                            anchor='w',
                            padding=5)
            lbl.grid(row=r, column=c, rowspan=rs, columnspan=cs, sticky='nsew')

        # 6) Enforce A4-width columns
        total_cols = 12
        col_min = self.a4_width // total_cols
        for col in range(total_cols):
            table_frame.grid_columnconfigure(col, weight=1, minsize=col_min)
        total_rows = max(r+rs for _, r, _, rs, _ in cells)
        for row in range(total_rows):
            table_frame.grid_rowconfigure(row, weight=1)

    def toggle_project_info(self):
        if hasattr(self, 'project_info_frame_visible') and self.project_info_frame_visible:
            self.project_info_container.grid_forget()
            self.toggle_info_btn.config(text="Show Project Info")
            self.content_frame.grid(row=1, column=0, sticky="nsew")
            self.project_info_frame_visible = False
        else:
            self.create_project_info_table()
            self.project_info_container.grid(row=1, column=0, sticky="nsew", pady=10)
            self.toggle_info_btn.config(text="Hide Project Info")
            self.content_frame.grid(row=2, column=0, sticky="nsew")
            self.project_info_frame_visible = True
            self.project_info_container.lift()  

    def EditSize(self, taille):
        self.root.taille = taille
        if self.current_page and isinstance(self.current_page, list):
            for text_widget in self.current_page:
                if hasattr(text_widget, 'configure'):
                    text_widget.configure(font=('Arial', self.root.taille))
                    text_widget.tag_configure("bold", font=('Arial', self.root.taille, 'bold'))

    def configure_tags(self):
        # Initialize bold tag for all existing text widgets
        for page in self.pages:
            for text_widget in page:
                text_widget.tag_configure("bold", font=('Arial', self.root.taille, 'bold'))


    # LES MATERIALS
    def create_log_box(self, parent, is_expandable=True):
        """
        Returns a dict for one box: { frame, handle, expandable, bg_color, texture }
        """
        box_frame = ttk.Frame(parent, style='LogBox.TFrame')
        # default state
        setattr(box_frame, 'bg_color', "#FFFFFF")
        setattr(box_frame, 'texture', "")

        # pack/draw as before…
        inner = tk.Frame(box_frame, bg=getattr(box_frame, 'bg_color', '#FFFFFF'), bd=1, relief="solid")
        inner.pack(fill="both", expand=True, padx=0, pady=0)

        # **bind click** on the outer frame
        box_frame.bind("<Button-1>", lambda e, b=box_frame: self.open_box_configurator(b))

        for w in (box_frame, inner):
            w.bind("<Button-1>", lambda e, b=box_frame: self.open_box_configurator(b))

        handle = None
        if is_expandable:
            handle = ttk.Frame(box_frame, height=5, cursor="sb_v_double_arrow")
            handle.pack(fill="x", side="bottom")

            # store local refs for closures
            min_h = self._log_min_height
            max_h = self._log_max_height

            def start_resize(e):
                setattr(handle, '_start_y', e.y_root)
                setattr(handle, '_start_h', box_frame.winfo_height())

            def do_resize(e):
                dy = e.y_root - getattr(handle, '_start_y', 0)
                new_h = getattr(handle, '_start_h', 0) + dy
                new_h = max(min_h, min(max_h, new_h))
                box_frame.place_configure(height=new_h)

            handle.bind("<ButtonPress-1>", start_resize)
            handle.bind("<B1-Motion>", do_resize)
        return {"frame": box_frame, "handle": handle, "expandable": bool(handle)}

    def add_log_box(self):
        """
        Called when the "Add Log" button is clicked.
        Finds the current page's log_container, freezes the previous expandable,
        then appends & places a fresh one.
        """
        if not self.log_boxes:
            print("WARNING: No log boxes structure found")
            return

        page_data = self.log_boxes[-1]
        
        # Check if container is valid
        if not page_data.get("container"):
            print("WARNING: No container found for current page")
            return
            
        try:
            # Test if container is still valid
            page_data["container"].winfo_exists()
        except Exception as e:
            print(f"ERROR: Container is invalid: {e}")
            return

        # freeze old expandable
        cur = page_data["current_expandable"]
        if cur and cur["handle"]:
            handle = cur["handle"]
            handle_height = handle.winfo_height()  
            current_height = cur["frame"].winfo_height()
            new_height = current_height - handle_height
            
            handle.destroy()
            cur["handle"] = None
            cur["expandable"] = False
            cur["frame"].place_configure(height=new_height) 

        # Update first box since its idle or what ever
        page_data["container"].update_idletasks()

        # now create & place the new one
        new_box = self.create_log_box(page_data["container"])
        y_offset = sum(b["frame"].winfo_height() for b in page_data["boxes"])
        new_box["frame"].place(relwidth=1, y=y_offset, height=self._log_min_height)
        page_data["boxes"].append(new_box)
        page_data["current_expandable"] = new_box

    def open_box_configurator(self, box_frame):
        """
        Pops up a dialog to choose geological material (with predefined colors) and texture for holes/structures.
        """
        win = tk.Toplevel(self.root)
        win.title("Configure Geological Log")
        win.transient(self.root)
        win.grab_set()
        win.geometry("400x500")

        # Geological materials with their predefined colors
        geological_materials = self.get_geological_materials_mapping()

        # Texture options for holes/structures
        texture_options = {
            "Remplissage uni": "",
            "Stratifications (----)": "----",
            "Fractures (||||)": "||||",
            "Cross-bedding (////)": "////",
            "Lamines ondulées (∿∿∿)": "∿∿∿",
            "Bioturbation (●●●)": "●●●",
            "Stylolithes (xxxx)": "xxxx",
            "Porosité vuggy (○ ○ ○)": "○ ○ ○",
            "Traces biologiques (+ + +)": "+ + +"
        }

        # Main frame
        main_frame = ttk.Frame(win, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Configuration du Log Géologique", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))

        # Material selection section
        material_frame = ttk.LabelFrame(main_frame, text="Type Lithologique", padding="10")
        material_frame.pack(fill="x", pady=(0, 10))

        # Create material selection with color preview
        material_var = tk.StringVar()
        current_bg_color = getattr(box_frame, 'bg_color', '#FFFFFF')
        
        # Find current material based on color
        current_material = "Autre"
        for material, color in geological_materials.items():
            if color.lower() == current_bg_color.lower():
                current_material = material
                break
        
        material_var.set(current_material)

        # Material dropdown with color preview
        material_label = ttk.Label(material_frame, text="Sélectionner le matériau:")
        material_label.pack(anchor="w", pady=(0, 5))

        material_combo_frame = ttk.Frame(material_frame)
        material_combo_frame.pack(fill="x", pady=(0, 10))

        material_combo = ttk.Combobox(
            material_combo_frame, 
            textvariable=material_var,
            values=list(geological_materials.keys()),
            state="readonly",
            width=25
        )
        material_combo.pack(side="left", fill="x", expand=True)

        # Color preview
        color_preview = tk.Frame(material_combo_frame, width=30, height=20, 
                                bg=geological_materials.get(current_material, '#FFFFFF'),
                                relief="solid", bd=1)
        color_preview.pack(side="right", padx=(10, 0))

        # Update color preview when material changes
        def update_color_preview(*args):
            selected_material = material_var.get()
            if selected_material in geological_materials:
                color = geological_materials[selected_material]
                color_preview.config(bg=color)

        material_var.trace("w", update_color_preview)

        # Texture selection section
        texture_frame = ttk.LabelFrame(main_frame, text="Texture / Structures", padding="10")
        texture_frame.pack(fill="x", pady=(0, 10))

        texture_label = ttk.Label(texture_frame, text="Sélectionner la texture (optionnel):")
        texture_label.pack(anchor="w", pady=(0, 5))

        texture_var = tk.StringVar()
        current_texture = getattr(box_frame, 'texture', '')
        
        # Find current texture
        current_texture_name = "Remplissage uni"
        for texture_name, texture_symbol in texture_options.items():
            if texture_symbol == current_texture:
                current_texture_name = texture_name
                break
        
        texture_var.set(current_texture_name)

        texture_combo = ttk.Combobox(
            texture_frame,
            textvariable=texture_var,
            values=list(texture_options.keys()),
            state="readonly"
        )
        texture_combo.pack(fill="x", pady=(0, 10))

        # Preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Aperçu", padding="10")
        preview_frame.pack(fill="both", expand=True, pady=(0, 10))

        preview_label = ttk.Label(preview_frame, text="Aperçu du log:")
        preview_label.pack(anchor="w", pady=(0, 5))

        # Preview box
        preview_box = tk.Frame(preview_frame, height=60, bg="#FFFFFF", 
                              relief="solid", bd=1)
        preview_box.pack(fill="x", pady=(0, 5))

        # Update preview function
        def update_preview(*args):
            selected_material = material_var.get()
            selected_texture = texture_var.get()
            
            # Update background color
            if selected_material in geological_materials:
                color = geological_materials[selected_material]
                preview_box.config(bg=color)
            
            # Update texture overlay
            # Remove existing texture
            for widget in preview_box.winfo_children():
                widget.destroy()
            
            # Add new texture if selected
            if selected_texture in texture_options and texture_options[selected_texture]:
                texture_symbol = texture_options[selected_texture]
                texture_label = tk.Label(
                    preview_box,
                    text=texture_symbol,
                    bg=color if selected_material in geological_materials else "#FFFFFF",
                    font=("Courier", 10),
                    bd=0, padx=0, pady=0,
                    justify="left", anchor="nw"
                )
                texture_label.place(relwidth=1, relheight=1)

        # Bind preview updates
        material_var.trace("w", update_preview)
        texture_var.trace("w", update_preview)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Apply button
        def apply_and_close():
            selected_material = material_var.get()
            selected_texture = texture_var.get()
            
            # Set background color
            if selected_material in geological_materials:
                color = geological_materials[selected_material]
                setattr(box_frame, 'bg_color', color)
                inner = box_frame.winfo_children()[0]
                inner.config(bg=color)
            
            # Set texture
            texture_symbol = texture_options.get(selected_texture, "")
            setattr(box_frame, 'texture', texture_symbol)
            
            # Update texture overlay
            inner = box_frame.winfo_children()[0]
            
            # Remove old texture overlay
            for w in inner.place_slaves():
                if w in self.texture_labels:
                    w.destroy()
                    del self.texture_labels[w]

            if texture_symbol:
                # Apply texture overlay
                font = ("Courier", 8)
                inner.update_idletasks()
                h = inner.winfo_height()
                line_h = inner.tk.call("font", "metrics", font, "-linespace") or 12
                # Calculate enough lines to fill the entire height with some padding
                count = max(int(h / line_h) + 2, 10)  # Add extra lines to ensure coverage

                txt = "\n".join([texture_symbol] * count)
                tex_label = tk.Label(
                    inner, text=txt,
                    bg=getattr(box_frame, 'bg_color', '#FFFFFF'),
                    font=font,
                    bd=0, padx=0, pady=0,
                    justify="left", anchor="nw"
                )
                self.texture_labels[tex_label] = True
                tex_label.place(relwidth=1, relheight=1)

            win.destroy()

        ok_btn = ttk.Button(buttons_frame, text="Appliquer", command=apply_and_close)
        ok_btn.pack(side="right", padx=(5, 0))

        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, text="Annuler", command=win.destroy)
        cancel_btn.pack(side="right")

        # Remove button
        def remove_and_close():
            # find & remove from the last page's list
            page = self.log_boxes[-1]
            for entry in page["boxes"]:
                if entry["frame"] is box_frame:
                    entry["frame"].destroy()
                    page["boxes"].remove(entry)
                    # if it was the expandable, clear it
                    if page["current_expandable"] is entry:
                        page["current_expandable"] = None
                    break
            win.destroy()

        remove_btn = ttk.Button(buttons_frame, text="Supprimer", command=remove_and_close)
        remove_btn.pack(side="left")

        # Initialize preview
        update_preview()

        # Center the popup
        win.update_idletasks()
        x = self.root.winfo_rootx() + 50
        y = self.root.winfo_rooty() + 50
        win.geometry(f"+{x}+{y}")

    def get_geological_materials_mapping(self):
        """Get the geological materials mapping for color/material name conversion"""
        return {
            "Grès / Sable": "#FFFF00",           # Jaune
            "Argile / Argileux": "#00FF00",      # Vert
            "Calcaire / Carbonaté": "#0000FF",   # Bleu
            "Dolomie": "#FF69B4",                # Rose
            "Siltite / Siltstone": "#D2B48C",    # Marron clair
            "Conglomérat": "#FFA500",            # Orange
            "Charbon": "#000000",                # Noir
            "Évaporites (gypse, sel)": "#F5F5F5", # Blanc / Gris très clair
            "Schiste (shale)": "#006400",        # Vert foncé
            "Calcaire siliceux (chert)": "#8A2BE2" # Violet
        }

    def get_geological_materials_reverse_mapping(self):
        """Get the reverse mapping from color to material name"""
        materials = self.get_geological_materials_mapping()
        return {color: name for name, color in materials.items()}

    def save_project(self):
        """Save the current project to a .sincus file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sincus",
            filetypes=[("Sincus Files", "*.sincus"), ("All Files", "*.*")],
            title="Sauvegarder le projet"
        )
        
        if not file_path:
            return
            
        try:
            # Prepare data for saving
            save_data = {
                'project_info': self.project_info,
                'pages_data': [],
                'log_boxes_data': [],
                'font_size': self.root.taille,
                'version': '1.0'
            }
            
            # Save text content from all pages
            for page in self.pages:
                page_data = []
                for text_widget in page:
                    # Get text content
                    text_content = text_widget.get("1.0", "end-1c")
                    
                    # Get bold formatting ranges
                    bold_ranges = []
                    start_idx = "1.0"
                    while True:
                        try:
                            range_start = text_widget.tag_nextrange("bold", start_idx)
                            if not range_start:
                                break
                            bold_ranges.append((range_start[0], range_start[1]))
                            start_idx = range_start[1]
                        except tk.TclError:
                            break
                    
                    page_data.append({
                        'content': text_content,
                        'bold_ranges': bold_ranges
                    })
                save_data['pages_data'].append(page_data)
            
            # Save log boxes data
            for page_log_boxes in self.log_boxes:
                page_boxes_data = []
                for box in page_log_boxes['boxes']:
                    # Get material name from color
                    bg_color = getattr(box['frame'], 'bg_color', '#FFFFFF')
                    material_name = "Autre"
                    
                    # Use reverse mapping to get material name
                    reverse_mapping = self.get_geological_materials_reverse_mapping()
                    if bg_color in reverse_mapping:
                        material_name = reverse_mapping[bg_color]
                    
                    box_data = {
                        'bg_color': bg_color,
                        'material_name': material_name,
                        'texture': getattr(box['frame'], 'texture', ''),
                        'height': box['frame'].winfo_height(),
                        'expandable': box.get('expandable', False)
                    }
                    page_boxes_data.append(box_data)
                save_data['log_boxes_data'].append(page_boxes_data)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Succès", f"Projet sauvegardé dans :\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde :\n{str(e)}")

    def load_project(self):
        """Load a project from a .sincus file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Sincus Files", "*.sincus"), ("All Files", "*.*")],
            title="Ouvrir un projet"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Clear current project
            self.clear_current_project()
            
            # Load project info
            self.project_info = save_data.get('project_info', {})
            self.TeteStart = int(re.sub(r'[^\d]', '', self.project_info.get('tete', '0')))
            
            # Load font size
            font_size = save_data.get('font_size', 12)
            self.root.taille = font_size
            
            # Recreate pages with loaded data
            pages_data = save_data.get('pages_data', [])
            for page_data in pages_data:
                # Create new page
                add_new_page(self)
                
                # Load text content and formatting
                current_page = self.pages[-1]
                for i, text_data in enumerate(page_data):
                    if i < len(current_page):
                        text_widget = current_page[i]
                        text_widget.delete("1.0", "end")
                        text_widget.insert("1.0", text_data.get('content', ''))
                        
                        # Apply bold formatting
                        for start, end in text_data.get('bold_ranges', []):
                            text_widget.tag_add("bold", start, end)
            
            # Load log boxes data
            log_boxes_data = save_data.get('log_boxes_data', [])
            for page_idx, page_boxes_data in enumerate(log_boxes_data):
                if page_idx < len(self.log_boxes):
                    page_log_boxes = self.log_boxes[page_idx]
                    
                    # Clear existing boxes
                    for box in page_log_boxes['boxes']:
                        box['frame'].destroy()
                    page_log_boxes['boxes'].clear()
                    
                    # Recreate boxes with saved data
                    for box_data in page_boxes_data:
                        new_box = self.create_log_box(page_log_boxes['container'])
                        bg_color = box_data.get('bg_color', '#FFFFFF')
                        texture = box_data.get('texture', '')
                        material_name = box_data.get('material_name', 'Autre')
                        
                        setattr(new_box['frame'], 'bg_color', bg_color)
                        setattr(new_box['frame'], 'texture', texture)
                        new_box['frame'].place(relwidth=1, height=box_data.get('height', 50))
                        
                        # Update inner frame color
                        inner = new_box['frame'].winfo_children()[0]
                        inner.config(bg=bg_color)
                        
                        # Apply texture overlay if texture exists
                        if texture:
                            # Remove any existing texture overlay
                            for w in inner.place_slaves():
                                if w in self.texture_labels:
                                    w.destroy()
                                    del self.texture_labels[w]
                            
                            # Apply texture overlay
                            font = ("Courier", 8)
                            inner.update_idletasks()
                            h = inner.winfo_height()
                            line_h = inner.tk.call("font", "metrics", font, "-linespace") or 12
                            # Calculate enough lines to fill the entire height with some padding
                            count = max(int(h / line_h) + 2, 10)  # Add extra lines to ensure coverage

                            txt = "\n".join([texture] * count)
                            tex_label = tk.Label(
                                inner, text=txt,
                                bg=bg_color,
                                font=font,
                                bd=0, padx=0, pady=0,
                                justify="left", anchor="nw"
                            )
                            self.texture_labels[tex_label] = True
                            tex_label.place(relwidth=1, relheight=1)
                        
                        page_log_boxes['boxes'].append(new_box)
            
            # Update status bar
            self.status_bar.config(text=f"Total pages: {len(self.pages)}")
            
            messagebox.showinfo("Succès", f"Projet chargé depuis :\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement :\n{str(e)}")

    def load_project_data(self, save_data):
        """Load project data from save_data (used when opening from splash screen)"""
        print("=== Starting load_project_data ===")
        try:
            # Load font size
            font_size = save_data.get('font_size', 12)
            self.root.taille = font_size
            print(f"Font size loaded: {font_size}")
            
            # Clear existing pages and log boxes
            print("Clearing existing project data...")
            self.clear_current_project()
            print("Project data cleared successfully")
            
            # IMPORTANT: Recreate the container after clearing
            print("Recreating container after clearing...")
            from gui.canvas import setup_canvas
            setup_canvas(self)
            print("Container recreated successfully")
            
            # Verify container is valid
            if self.container is None:
                print("ERROR: Container is still None after recreation")
                messagebox.showerror("Erreur", "Impossible de créer le conteneur principal")
                return
            
            try:
                self.container.winfo_exists()
                print("Container is valid and ready")
            except Exception as e:
                print(f"ERROR: Container is still invalid: {e}")
                messagebox.showerror("Erreur", "Le conteneur principal est invalide")
                return
            
            # Small delay to ensure widgets are properly created
            self.root.update_idletasks()
            print("Container setup completed, proceeding with page creation")
            
            # Recreate pages with loaded data
            pages_data = save_data.get('pages_data', [])
            print(f"Found {len(pages_data)} pages to load")
            
            for page_idx, page_data in enumerate(pages_data):
                print(f"Creating page {page_idx + 1}...")
                try:
                    # Create new page
                    add_new_page(self)
                    print(f"Page {page_idx + 1} created successfully")
                    
                    # Load text content and formatting
                    current_page = self.pages[-1]
                    print(f"Loading text content for page {page_idx + 1}...")
                    for i, text_data in enumerate(page_data):
                        if i < len(current_page):
                            text_widget = current_page[i]
                            content = text_data.get('content', '')
                            text_widget.delete("1.0", "end")
                            text_widget.insert("1.0", content)
                            print(f"  Text widget {i}: loaded content (length: {len(content)})")
                            
                            # Apply bold formatting
                            bold_ranges = text_data.get('bold_ranges', [])
                            for start, end in bold_ranges:
                                text_widget.tag_add("bold", start, end)
                            print(f"  Text widget {i}: applied {len(bold_ranges)} bold ranges")
                except Exception as e:
                    print(f"ERROR creating page {page_idx + 1}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continue with next page instead of failing completely
                    continue
            
            print("Text content loading completed")
            
            # Now that pages are created, log boxes structure should be available
            print(f"After page creation: {len(self.log_boxes)} log box pages available")
            
            # Load log boxes data with more robust approach
            print("Starting log boxes loading process...")
            self._load_log_boxes_data_robust(save_data)
            
        except Exception as e:
            print(f"ERROR in load_project_data: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données :\n{str(e)}")

    def _load_log_boxes_data_robust(self, save_data):
        """More robust log boxes loading with extensive error checking"""
        print("=== Starting _load_log_boxes_data_robust ===")
        try:
            log_boxes_data = save_data.get('log_boxes_data', [])
            print(f"Found log boxes data for {len(log_boxes_data)} pages")
            
            # Ensure we have log boxes to work with
            if not self.log_boxes:
                print("WARNING: No log boxes found, but we have log boxes data to load")
                print("This might happen if pages were created but log boxes weren't initialized")
                print("Attempting to recreate log boxes structure...")
                
                # Recreate log boxes structure for existing pages
                if log_boxes_data and len(self.pages) > 0:
                    print("Recreating log boxes structure for existing pages...")
                    for page_idx in range(len(self.pages)):
                        if page_idx < len(log_boxes_data):
                            print(f"Recreating log boxes structure for page {page_idx + 1}...")
                            try:
                                # Get the page frame from the container
                                if self.container is None:
                                    raise Exception("Container is None")
                                page_frame = self.container.winfo_children()[page_idx]
                                # Find the log container (second column, index 1)
                                log_container = page_frame.winfo_children()[1].winfo_children()[1]
                                
                                # Create log boxes structure for this page
                                self.log_boxes.append({
                                    'container': log_container,
                                    'boxes': [],
                                    'current_expandable': None
                                })
                                print(f"Log boxes structure created for page {page_idx + 1}")
                            except Exception as e:
                                print(f"ERROR creating log boxes structure for page {page_idx + 1}: {e}")
                                # Create empty structure as fallback
                                self.log_boxes.append({
                                    'container': None,
                                    'boxes': [],
                                    'current_expandable': None
                                })
                        else:
                            # Create empty structure for pages without log boxes data
                            self.log_boxes.append({
                                'container': None,
                                'boxes': [],
                                'current_expandable': None
                            })
                
                print(f"Recreated log boxes structure with {len(self.log_boxes)} entries")
            
            print(f"Current log_boxes structure: {len(self.log_boxes)} entries")
            
            # Clear existing log boxes first
            print("Clearing existing log boxes...")
            for page_idx, page_log_boxes in enumerate(self.log_boxes):
                print(f"  Clearing log boxes for page {page_idx + 1}...")
                for box_idx, box in enumerate(page_log_boxes.get('boxes', [])):
                    try:
                        if 'frame' in box and box['frame']:
                            box['frame'].destroy()
                            print(f"    Box {box_idx} destroyed successfully")
                    except Exception as e:
                        print(f"    WARNING: Could not destroy box {box_idx}: {e}")
                page_log_boxes['boxes'] = []
            print("Existing log boxes cleared")
            
            for page_idx, page_boxes_data in enumerate(log_boxes_data):
                print(f"Processing log boxes for page {page_idx}...")
                
                if page_idx >= len(self.log_boxes):
                    print(f"WARNING: Page {page_idx} not found in log_boxes, skipping")
                    continue
                
                page_log_boxes = self.log_boxes[page_idx]
                print(f"Page log boxes structure: {page_log_boxes}")
                
                # Check if container exists and is valid
                if 'container' not in page_log_boxes:
                    print(f"ERROR: No container found for page {page_idx}")
                    continue
                
                container = page_log_boxes['container']
                print(f"Container found: {container}")
                
                try:
                    # Test if container is still valid
                    container.winfo_exists()
                    print("Container is valid")
                except Exception as e:
                    print(f"ERROR: Container is invalid: {e}")
                    continue
                
                # Recreate boxes with saved data
                print(f"Creating {len(page_boxes_data)} new boxes...")
                y_offset = 0  # Start at the top
                
                for box_idx, box_data in enumerate(page_boxes_data):
                    try:
                        print(f"  Creating box {box_idx + 1}...")
                        
                        # Create new box - make all boxes non-expandable initially
                        is_last_box = (box_idx == len(page_boxes_data) - 1)
                        new_box = self.create_log_box(container, is_expandable=is_last_box)
                        print(f"    Box created successfully (expandable: {is_last_box})")
                        
                        # Set properties
                        bg_color = box_data.get('bg_color', '#FFFFFF')
                        texture = box_data.get('texture', '')
                        height = box_data.get('height', 50)
                        material_name = box_data.get('material_name', 'Autre')
                        
                        setattr(new_box['frame'], 'bg_color', bg_color)
                        setattr(new_box['frame'], 'texture', texture)
                        
                        print(f"    Properties set: bg_color={bg_color}, material={material_name}, texture={texture}, height={height}")
                        print(f"    Positioning at y={y_offset}")
                        
                        # Place the box at the calculated y position
                        new_box['frame'].place(relwidth=1, y=y_offset, height=height)
                        print(f"    Box placed successfully at y={y_offset}")
                        
                        # Update inner frame color
                        try:
                            inner = new_box['frame'].winfo_children()[0]
                            inner.config(bg=bg_color)
                            print(f"    Inner frame color updated")
                        except Exception as e:
                            print(f"    WARNING: Could not update inner frame color: {e}")
                        
                        # Apply texture overlay if texture exists
                        if texture:
                            try:
                                # Remove any existing texture overlay
                                for w in inner.place_slaves():
                                    if w in self.texture_labels:
                                        w.destroy()
                                        del self.texture_labels[w]
                                
                                # Apply texture overlay
                                font = ("Courier", 8)
                                inner.update_idletasks()
                                h = inner.winfo_height()
                                line_h = inner.tk.call("font", "metrics", font, "-linespace") or 12
                                # Calculate enough lines to fill the entire height with some padding
                                count = max(int(h / line_h) + 2, 10)  # Add extra lines to ensure coverage

                                txt = "\n".join([texture] * count)
                                tex_label = tk.Label(
                                    inner, text=txt,
                                    bg=bg_color,
                                    font=font,
                                    bd=0, padx=0, pady=0,
                                    justify="left", anchor="nw"
                                )
                                self.texture_labels[tex_label] = True
                                tex_label.place(relwidth=1, relheight=1)
                                print(f"    Texture overlay applied")
                            except Exception as e:
                                print(f"    WARNING: Could not apply texture overlay: {e}")
                        
                        page_log_boxes['boxes'].append(new_box)
                        print(f"    Box {box_idx + 1} added to page")
                        
                        # Calculate y position for next box
                        y_offset += height
                        print(f"    Next box will start at y={y_offset}")
                        
                    except Exception as e:
                        print(f"    ERROR creating box {box_idx + 1}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                # Set the current_expandable to the last box created (if any boxes were created)
                if page_log_boxes['boxes']:
                    page_log_boxes['current_expandable'] = page_log_boxes['boxes'][-1]
                    print(f"Set current_expandable to last box for page {page_idx}")
                else:
                    page_log_boxes['current_expandable'] = None
                    print(f"No boxes created for page {page_idx}, current_expandable set to None")
                
                print(f"Page {page_idx} log boxes processing completed")
            
            # Update status bar
            self.status_bar.config(text=f"Total pages: {len(self.pages)}")
            print("Status bar updated")
            
            print("=== Log boxes loading completed successfully ===")
            messagebox.showinfo("Succès", "Projet chargé avec succès!")
            
        except Exception as e:
            print(f"ERROR in _load_log_boxes_data_robust: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Erreur lors du chargement des log boxes :\n{str(e)}")

    def clear_current_project(self):
        """Clear the current project data"""
        print("=== Starting clear_current_project ===")
        try:
            # Clear pages
            print(f"Clearing {len(self.pages)} pages...")
            for page_idx, page in enumerate(self.pages):
                print(f"  Clearing page {page_idx + 1}...")
                for widget_idx, text_widget in enumerate(page):
                    try:
                        text_widget.destroy()
                        print(f"    Text widget {widget_idx} destroyed successfully")
                    except Exception as e:
                        print(f"    WARNING: Could not destroy text widget {widget_idx}: {e}")
            self.pages.clear()
            print("Pages cleared")
            
            # Clear log boxes
            print(f"Clearing {len(self.log_boxes)} log box pages...")
            for page_idx, page_log_boxes in enumerate(self.log_boxes):
                print(f"  Clearing log boxes for page {page_idx + 1}...")
                for box_idx, box in enumerate(page_log_boxes['boxes']):
                    try:
                        box['frame'].destroy()
                        print(f"    Log box {box_idx} destroyed successfully")
                    except Exception as e:
                        print(f"    WARNING: Could not destroy log box {box_idx}: {e}")
            self.log_boxes.clear()
            print("Log boxes cleared")
            
            # Clear content frame
            print("Clearing content frame...")
            content_widgets = self.content_frame.winfo_children()
            print(f"  Found {len(content_widgets)} widgets in content frame")
            for widget_idx, widget in enumerate(content_widgets):
                try:
                    widget.destroy()
                    print(f"    Content widget {widget_idx} destroyed successfully")
                except Exception as e:
                    print(f"    WARNING: Could not destroy content widget {widget_idx}: {e}")
            
            print("=== clear_current_project completed successfully ===")
        except Exception as e:
            print(f"ERROR in clear_current_project: {e}")
            import traceback
            traceback.print_exc()

    def is_initialized(self):
        """Check if the app is properly initialized"""
        print("=== Checking if app is initialized ===")
        has_container = hasattr(self, 'container') and self.container is not None
        has_pages = hasattr(self, 'pages') and len(self.pages) > 0
        print(f"  Has container: {has_container}")
        print(f"  Has pages: {has_pages} (count: {len(self.pages) if hasattr(self, 'pages') else 0})")
        result = has_container and has_pages
        print(f"  App initialized: {result}")
        return result

    def return_to_splash(self):
        """Return to the splash screen"""
        from tkinter import messagebox
        response = messagebox.askyesno(
            "Retour à l'accueil",
            "Voulez-vous vraiment retourner à l'écran d'accueil ?\n\nTout travail non sauvegardé sera perdu.",
            icon='warning'
        )
        if response:
            # Clear the current app
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Reset grid configuration
            for i in range(self.root.grid_size()[0]):
                self.root.columnconfigure(i, weight=0)
            for i in range(self.root.grid_size()[1]):
                self.root.rowconfigure(i, weight=0)
            
            # Create new splash window
            def on_splash_create(jwt_token=None):
                from gui.project_info import ProjectInfoWindow
                ProjectInfoWindow(self.root, start_main_app, jwt_token=jwt_token)
            
            def start_main_app(project_info, jwt_token=None):
                from core.app import Sincus
                # Update global token if provided
                if jwt_token:
                    from utils.auth_state import set_jwt_token_global
                    set_jwt_token_global(jwt_token)
                
                # Destroy any existing widgets
                for widget in self.root.winfo_children():
                    widget.destroy()
                
                # Start main application with global JWT token
                new_app = Sincus(self.root, project_info, get_jwt_token_global())
            
            from gui.splash import SplashWindow
            SplashWindow(self.root, on_splash_create)


