import tkinter as tk
from tkinter import ttk

class ProjectInfoWindow:
    def __init__(self, master, on_submit_callback):
        self.master = master
        self.on_submit = on_submit_callback
        self.master.title("Project Information")
        self.master.resizable(False, False)

        # Default values
        self.default_values = {
            'carotte_summary': "Carotté : 18 m \nRécupéré : 18m soit 100% \nDate d'extraction de la carotte: 27/06/17",
            'puits': "Nord West Trig-2",
            'sigle': "NWT-2",
            'permis': "Ohanet II",
            'bloc': "234a",
            'echelle': "1/40",
            'carottier': "12440525",
            'mud_type': "OBM",
            'carotte': "11",
            'couronne': "6\" x 2 5/8\"",
            'd_value': "1,08",
            'tete': "2930m",
            'core_type': "Ci3126",
            'fun_vis': "46",
            'pied': "3948m"
        }

        # Main container
        self.container = ttk.Frame(self.master)
        self.container.pack(padx=20, pady=20)

        self.form_frame = ttk.Frame(self.container)
        self.form_frame.pack()

        self.button_frame = ttk.Frame(self.container)
        self.button_frame.pack(fill='x', pady=10)

        self.create_form()

        # Confirm Button (Green)
        self.confirm_btn = tk.Button(
            self.button_frame,
            text="Confirmer",
            command=self.on_confirm,
            bg="#4CAF50",
            fg="white",
            borderwidth=0,
            padx=10,
            pady=5
        )
        self.confirm_btn.pack(side=tk.RIGHT, padx=10)
        self.confirm_btn.bind("<Enter>", lambda e: self.confirm_btn.config(bg="#45a049"))
        self.confirm_btn.bind("<Leave>", lambda e: self.confirm_btn.config(bg="#4CAF50"))

        # Cancel Button (Red)
        self.cancel_btn = tk.Button(
            self.button_frame,
            text="Annuler",
            command=self.on_cancel,
            bg="#f44336",
            fg="white",
            borderwidth=0,
            padx=10,
            pady=5
        )
        self.cancel_btn.pack(side=tk.RIGHT)
        self.cancel_btn.bind("<Enter>", lambda e: self.cancel_btn.config(bg="#d32f2f"))
        self.cancel_btn.bind("<Leave>", lambda e: self.cancel_btn.config(bg="#f44336"))

        # MAKE WINDOW ON CENTER OF SCREEN
        self.master.update_idletasks()
        width = self.master.winfo_reqwidth()
        height = self.master.winfo_reqheight()

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def create_form(self):
        """Create form fields for project information"""
        fields = [
            ("Puits", "puits"),
            ("Sigle", "sigle"),
            ("Permis", "permis"),
            ("Bloc", "bloc"),
            ("Echelle", "echelle"),
            ("Carottier", "carottier"),
            ("Mud Type", "mud_type"),
            ("Carotte", "carotte"),
            ("Couronne", "couronne"),
            ("D Value", "d_value"),
            ("Tête", "tete"),
            ("Core Type", "core_type"),
            ("Fun Vis", "fun_vis"),
            ("Pied", "pied"),
        ]

        self.entries = {}

        # Container for form fields
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack()

        # Configure grid for 3 columns
        for i in range(3):
            form_grid.columnconfigure(i, weight=1)

        # Create form elements - 3 per row
        for index, (label_text, field_name) in enumerate(fields):
            row = index // 3
            col = index % 3

            frame = ttk.Frame(form_grid)
            frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")

            label = ttk.Label(frame, text=label_text)
            label.pack(anchor=tk.W)

            entry = ttk.Entry(frame, width=20)
            entry.insert(0, self.default_values.get(field_name, ""))
            entry.pack(fill=tk.X)
            self.entries[field_name] = entry

        # Special multi-line field for carotte summary
        carotte_label = ttk.Label(form_grid, text="Sommaire de la fiche carotte")
        carotte_label.grid(row=100, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        self.carotte_text = tk.Text(form_grid, height=5, width=50)
        self.carotte_text.insert("1.0", self.default_values.get("carotte_summary", ""))
        self.carotte_text.grid(row=101, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

    def on_confirm(self):
        """Handle confirm button click"""
        project_info = {
            field: entry.get() for field, entry in self.entries.items()
        }
        project_info["carotte_summary"] = self.carotte_text.get("1.0", tk.END).strip()

        self.master.resizable(True, True)
        self.form_frame.destroy()
        self.on_submit(project_info)

    def on_cancel(self):
        """Handle cancel button click - destroy root window"""
        self.master.destroy()
