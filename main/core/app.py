import tkinter as tk
import re
from tkinter import ttk, colorchooser
from gui.controls import setup_controls
from gui.canvas import setup_canvas
from utils.styles import setup_styles
from functions.new_page import add_new_page
from reportlab.lib.pagesizes import A4

class Sincus:
    def __init__(self, root, project_info):
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
        
        # Setup components
        setup_styles()
        setup_controls(self)
        setup_canvas(self)
        add_new_page(self)
        self.configure_tags()

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
        if self.current_page:
            for text_widget in self.current_page:
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
        box_frame.bg_color = "#FFFFFF"
        box_frame.texture = ""  

        # pack/draw as before…
        inner = tk.Frame(box_frame, bg=box_frame.bg_color, bd=1, relief="solid")
        inner.pack(fill="both", expand=True)

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
                handle._start_y = e.y_root
                handle._start_h = box_frame.winfo_height()

            def do_resize(e):
                dy = e.y_root - handle._start_y
                new_h = handle._start_h + dy
                new_h = max(min_h, min(max_h, new_h))
                box_frame.place_configure(height=new_h)

            handle.bind("<ButtonPress-1>", start_resize)
            handle.bind("<B1-Motion>", do_resize)
        return {"frame": box_frame, "handle": handle, "expandable": bool(handle)}

    def add_log_box(self):
        """
        Called when the “+ Add Log” button is clicked.
        Finds the current page’s log_container, freezes the previous expandable,
        then appends & places a fresh one.
        """
        if not self.log_boxes:
            return

        page_data = self.log_boxes[-1]

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
        Pops up a small dialog to choose bg color, texture, or remove the box.
        """
        win = tk.Toplevel(self.root)
        win.title("Configure Box")
        win.transient(self.root)
        win.grab_set()

        # — Color chooser —
        def pick_color():
            c = colorchooser.askcolor(initialcolor=box_frame.bg_color, parent=win)
            if c and c[1]:
                box_frame.bg_color = c[1]
                inner = box_frame.winfo_children()[0]
                inner.config(bg=box_frame.bg_color)

        ttk.Button(win, text="Choose Color…", command=pick_color)\
            .pack(fill="x", padx=10, pady=(10,5))

        # — Texture dropdown —
        textures = ["++++", "-----", "//////", "-+-+-+-+", "--.--."]
        tex_var = tk.StringVar(value=box_frame.texture)
        ttk.Label(win, text="Texture:").pack(anchor="w", padx=10)
        combo = ttk.Combobox(
            win, textvariable=tex_var,
            values=textures, state="readonly"
        )
        combo.pack(fill="x", padx=10, pady=(0,10))

        # — Apply (OK) —
        def apply_and_close():
            box_frame.texture = tex_var.get()
            inner = box_frame.winfo_children()[0]

            # remove old texture overlay
            for w in inner.place_slaves():
                if getattr(w, "_is_texture", False):
                    w.destroy()

            if box_frame.texture:
                # tile vertically to fill the height
                # approximate line count from box height / font height
                font = ("Courier", 8)
                # force an update to get actual height
                inner.update_idletasks()
                h = inner.winfo_height()
                # rough line‐height in pixels
                line_h = inner.tk.call("font", "metrics", font, "-linespace") or 12
                count = max(int(h / line_h) + 1, 5)

                txt = "\n".join([box_frame.texture] * count)
                tex_label = tk.Label(
                    inner, text=txt,
                    bg=box_frame.bg_color,
                    font=font,
                    bd=0, padx=0, pady=0,
                    justify="left", anchor="nw"
                )
                tex_label._is_texture = True
                tex_label.place(relwidth=1, relheight=1)

            win.destroy()

        ok_btn = ttk.Button(win, text="OK", command=apply_and_close)
        ok_btn.pack(side="right", padx=(0,10), pady=(0,10))

        # — Remove button —
        def remove_and_close():
            # find & remove from the last page’s list
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

        remove_btn = ttk.Button(win, text="Remove Box", command=remove_and_close)
        remove_btn.pack(side="left", padx=(10,0), pady=(0,10))

        # Center the popup
        win.update_idletasks()
        x = self.root.winfo_rootx() + 50
        y = self.root.winfo_rooty() + 50
        win.geometry(f"+{x}+{y}")


