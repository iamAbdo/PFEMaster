import tkinter as tk
from tkinter import ttk
from tkinter import font

class SplashWindow:
    def __init__(self, master, on_create_callback):
        self.master = master
        self.on_create = on_create_callback
        self.master.state('zoomed')
        self.master.title("Welcome")
        
        # self.master.resizable(False, False)

        # single row for content
        self.master.rowconfigure(0, weight=1)
        # two columns: left and right (left:1, right:2)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=4)

        # prepare consistent fonts for labels
        self.label_font = font.Font(family="TkDefaultFont", size=10)
        self.hover_font = font.Font(family="TkDefaultFont", size=10, underline=1)

        # Left part with right border
        left = ttk.Frame(master, padding=(10,10,0,10))
        left.grid(row=0, column=0, sticky='nsew')
        # content area inside left
        content = ttk.Frame(left)
        content.pack(side='left', fill='both', expand=True)
        # right-side thick gray border
        border_line = tk.Frame(left, width=2, bg='gray')
        border_line.pack(side='right', fill='y')

        for text in ("Settings", "Account"):
            lbl = tk.Label(
                content,
                text=text,
                cursor='hand2',
                font=self.label_font,
                width=15,
                anchor='w'
            )
            lbl.pack(anchor='nw', pady=5)
            lbl.bind("<Enter>", lambda e, l=lbl: l.config(font=self.hover_font, fg="blue"))
            lbl.bind("<Leave>", lambda e, l=lbl: l.config(font=self.label_font, fg="black"))
            lbl.bind("<Button-1>", lambda e: None)

        # Right part (project actions) with left padding for gap
        right = ttk.Frame(master, padding=(20,10,10,10)) # , style='Blue.TFrame')
        right.grid(row=0, column=1, sticky='nsew')

        # style = ttk.Style()
        # style.configure('Blue.TFrame', background='#e6f3ff')

        right.columnconfigure(0, weight=1)

        # Description and horizontal line
        desc = tk.Label(right, text="Project Management", font=(None, 14))
        desc.grid(row=0, column=0, pady=(0,5), sticky='w')  
        hr = ttk.Separator(right, orient='horizontal')
        hr.grid(row=1, column=0, sticky='ew', pady=(0,10))

        self.master.update_idletasks()
        screen_h = self.master.winfo_screenheight()
        square = int(screen_h * 0.35)

        # Create a container frame for the buttons
        button_frame = ttk.Frame(right)
        button_frame.grid(row=2, column=0, sticky='w')

        # Create New Project button container
        create_btn = tk.Frame(
            button_frame,  # Changed parent to button_frame
            width=square,
            height=square,
            relief='raised',
            borderwidth=2,
            cursor='hand2'
        )
        create_btn.grid(row=0, column=0, sticky='w', padx=(0,10))  # Now in column 0 of button_frame
        create_btn.grid_propagate(False)
        plus = tk.Label(create_btn, text="+", font=("Arial", 48), fg="gray")
        plus.pack(expand=True)
        txt = tk.Label(create_btn, text="Create new project")
        txt.pack(side='bottom', pady=10)
        for widget in (create_btn, plus, txt):
            widget.bind("<Button-1>", lambda e: self._create())

        # Open Existing Project button container
        open_btn = tk.Frame(
            button_frame,  # Changed parent to button_frame
            width=square,
            height=square,
            relief='raised',
            borderwidth=2,
            cursor='hand2'
        )
        open_btn.grid(row=0, column=1, sticky='w')  # Now in column 1 of button_frame
        open_btn.grid_propagate(False)

        folder = tk.Label(open_btn, text="📁", font=("Arial", 48), fg="gray")
        folder.pack(expand=True)
        txt2 = tk.Label(open_btn, text="Open existing project")
        txt2.pack(side='bottom', pady=10)
        for widget in (open_btn, folder, txt2):
            widget.bind("<Button-1>", lambda e: None)  # Placeholder for future functionality

    def _create(self):
        # restore normal window state before next window
        self.master.state('normal')
        # destroy splash layout
        for widget in self.master.winfo_children():
            widget.destroy()

        # Reset grid configuration (critical!)
        for i in range(self.master.grid_size()[0]):  # Clear column weights
            self.master.columnconfigure(i, weight=0)
        for i in range(self.master.grid_size()[1]):  # Clear row weights
            self.master.rowconfigure(i, weight=0)
        # call callback to open project info
        self.on_create()
