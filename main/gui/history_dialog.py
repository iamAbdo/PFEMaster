import tkinter as tk
from tkinter import ttk, messagebox
import requests
from utils.auth_state import get_jwt_token_global
from datetime import datetime

class HistoryDialog:
    def __init__(self, parent):
        self.parent = parent
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Historique des activités")
        self.dialog.geometry("1000x600")
        self.dialog.configure(bg='#f0f0f0')
        self.dialog.resizable(True, True)
        self.dialog.minsize(800, 500)
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"1000x600+{x}+{y}")
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.dialog, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="Historique des activités système",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0'
        ).pack(side='left')
        
        # Refresh button
        refresh_btn = tk.Button(
            header_frame,
            text="Actualiser",
            command=self.load_data,
            bg='#3498db',
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        )
        refresh_btn.pack(side='right')
        
        # Create treeview
        columns = ('Date/Heure', 'Utilisateur', 'Action', 'Détails', 'Statut', 'IP')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.tree.heading('Date/Heure', text='Date/Heure')
        self.tree.heading('Utilisateur', text='Utilisateur')
        self.tree.heading('Action', text='Action')
        self.tree.heading('Détails', text='Détails')
        self.tree.heading('Statut', text='Statut')
        self.tree.heading('IP', text='Adresse IP')
        
        self.tree.column('Date/Heure', width=150, anchor='center')
        self.tree.column('Utilisateur', width=150, anchor='w')
        self.tree.column('Action', width=120, anchor='w')
        self.tree.column('Détails', width=300, anchor='w')
        self.tree.column('Statut', width=80, anchor='center')
        self.tree.column('IP', width=120, anchor='center')
        
        # Configure row styling
        self.tree.tag_configure('success', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('error', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('warning', background='#fff3cd', foreground='#856404')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Chargement...",
            font=("Arial", 9),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(side='bottom', pady=(10, 0))

    def load_data(self):
        """Load activity logs from the backend"""
        try:
            jwt_token = get_jwt_token_global()
            if not jwt_token:
                messagebox.showerror("Erreur", "Vous devez être connecté pour voir l'historique")
                return
            
            headers = {'Authorization': f'Bearer {jwt_token}'}
            response = requests.get(
                'https://127.0.0.1:5000/api/user/activity-logs',
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                logs = data.get('logs', [])
                
                # Clear existing items
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Add logs to treeview
                for log in logs:
                    # Format date
                    created_at = log.get('created_at', '')
                    if created_at:
                        try:
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            formatted_date = dt.strftime('%d/%m/%Y %H:%M:%S')
                        except:
                            formatted_date = created_at
                    else:
                        formatted_date = 'N/A'
                    
                    # Get status tag
                    status = log.get('status', 'unknown')
                    if status == 'success':
                        tag = 'success'
                    elif status == 'error':
                        tag = 'error'
                    elif status == 'warning':
                        tag = 'warning'
                    else:
                        tag = ''
                    
                    self.tree.insert('', 'end', values=(
                        formatted_date,
                        log.get('user_email', 'Unknown'),
                        log.get('action', 'Unknown'),
                        log.get('details', ''),
                        status.upper(),
                        log.get('ip_address', 'N/A')
                    ), tags=(tag,))
                
                self.status_label.config(text=f"{len(logs)} activités chargées")
                
            elif response.status_code == 403:
                messagebox.showerror("Erreur", "Vous n'avez pas les permissions pour voir l'historique")
            else:
                messagebox.showerror("Erreur", f"Erreur lors du chargement: {response.text}")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
            self.status_label.config(text="Erreur de chargement")

    def show(self):
        """Show the dialog and wait for it to close"""
        self.dialog.wait_window()


def show_history_dialog(parent):
    """Show the history dialog"""
    return HistoryDialog(parent).show() 