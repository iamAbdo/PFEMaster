import tkinter as tk
from tkinter import ttk
import requests

class ProjectInfoWindow:
    def __init__(self, master, on_submit_callback, jwt_token=None):
        self.master = master
        self.on_submit = on_submit_callback
        self.jwt_token = jwt_token
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

        self.zones = None
        if self.jwt_token:
            self.fetch_zones()
        else:
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

    def fetch_zones(self):
        try:
            headers = {'Authorization': f'Bearer {self.jwt_token}'}
            resp = requests.get('https://127.0.0.1:5000/api/zone/zones', headers=headers, verify=False)
            if resp.status_code == 200:
                zones = resp.json().get('zones', [])
                if zones is None:
                    self.zones = []
                else:
                    self.zones = zones
            else:
                self.zones = []
            self.create_form()
        except Exception:
            self.zones = []
            self.create_form()

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

        zones_list = self.zones if self.zones is not None else []
        # If zones are available, use dropdown for first 4 fields
        if zones_list and len(zones_list) > 0:
            print('logged in')
            # Prepare zone options as strings
            zone_options = [f"{z['sigle']} | {z['puits']} | {z['bloc']} | {z['permis']}" for z in zones_list]
            self.zone_var = tk.StringVar()
            # Default to first zone
            self.zone_var.set(zone_options[0])
            def on_zone_select(event=None):
                idx = zone_options.index(self.zone_var.get())
                zone = zones_list[idx]
                for i, key in enumerate(['puits', 'sigle', 'permis', 'bloc']):
                    entry = self.entries[key]
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, zone[key])
                    entry.config(state='readonly')
            # Add dropdown at the top
            zone_label = ttk.Label(form_grid, text="Zone (Sigle | Puits | Bloc | Permis)")
            zone_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")
            zone_combo = ttk.Combobox(form_grid, textvariable=self.zone_var, values=zone_options, state="readonly", width=50)
            zone_combo.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
            zone_combo.bind("<<ComboboxSelected>>", on_zone_select)
            # Create the first 4 fields as readonly entries
            for index, (label_text, field_name) in enumerate(fields[:4]):
                # Start from row 2 (after dropdown) and use 3-column layout
                row = 2 + (index // 3)
                col = index % 3
                frame = ttk.Frame(form_grid)
                frame.grid(row=row, column=col, padx=10, pady=5, sticky="nsew")
                label = ttk.Label(frame, text=label_text)
                label.pack(anchor=tk.W)
                entry = ttk.Entry(frame, width=20, state='readonly')
                entry.pack(fill=tk.X)
                self.entries[field_name] = entry
            # Fill with first zone by default
            def fill_first_zone():
                zone = zones_list[0]
                for key in ['puits', 'sigle', 'permis', 'bloc']:
                    entry = self.entries[key]
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, zone[key])
                    entry.config(state='readonly')
            fill_first_zone()
            # Continue with the rest of the fields
            start_idx = 4
        else:
            # Create form elements - 3 per row
            for index, (label_text, field_name) in enumerate(fields[:4]):
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
            start_idx = 4
        # Continue with the rest of the fields
        for index, (label_text, field_name) in enumerate(fields[start_idx:], start=start_idx):
            if zones_list and len(zones_list) > 0:
                # When zones are available, start from row 2 and continue the 3-column layout
                # The first 4 fields take rows 2 and 3, so remaining fields start from row 4
                adjusted_index = index - 4  # Adjust for the first 4 fields
                row = 4 + (adjusted_index // 3)
                col = adjusted_index % 3
            else:
                # When no zones, use normal positioning
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
        if zones_list and len(zones_list) > 0:
            # When zones are available, calculate the last row used by form fields
            # First 4 fields: rows 2-3, remaining fields: starting from row 4
            remaining_fields_count = len(fields) - 4
            last_form_row = 4 + (remaining_fields_count - 1) // 3
            carotte_label.grid(row=last_form_row + 1, column=0, columnspan=3, padx=10, pady=5, sticky="w")
            self.carotte_text = tk.Text(form_grid, height=5, width=50)
            self.carotte_text.insert("1.0", self.default_values.get("carotte_summary", ""))
            self.carotte_text.grid(row=last_form_row + 2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        else:
            # When no zones, use normal positioning
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
        """Handle cancel button click - go back to splash screen"""
        # Clear the current window
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Reset window configuration
        self.master.state('normal')
        for i in range(self.master.grid_size()[0]):
            self.master.columnconfigure(i, weight=0)
        for i in range(self.master.grid_size()[1]):
            self.master.rowconfigure(i, weight=0)
        
        # Recreate splash screen
        from gui.splash import SplashWindow
        def on_splash_create(jwt_token=None):
            ProjectInfoWindow(self.master, self.on_submit, jwt_token=jwt_token)
        
        # Create a new splash window
        splash = SplashWindow(self.master, on_splash_create)
