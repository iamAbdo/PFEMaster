
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Fix font issues
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))  
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))


# Custom styles
styles = {
    'header': ParagraphStyle(
        'header',
        fontName='Arial-Bold',
        fontSize=10,
        leading=12,
    ),
    'normal': ParagraphStyle(
        'normal',
        fontName='Arial',
        fontSize=9,
        leading=10,
    ),
    'table_header': ParagraphStyle(
        'table_header',
        fontName='Arial-Bold',
        fontSize=8,
        leading=9,
    ),
    'table_text': ParagraphStyle(
        'table_text',
        fontName='Arial',
        fontSize=8,
        leading=9,
    )
}

def create_core_document(output_filename, data):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    story = []
    
    # Header Section
    header_data = [
        ["Puits :", data['puits'], "Sigle :", data['sigle']],
        ["Permis :", data['permis'], "Bloc :", data['bloc']],
        ["Carottier:", data['carottier'], "Type de Boue :", data['type_boue'], "CAROTTE :", data['carotte_num']],
        ["Couronne:", data['couronne'], "D :", data['d'], "TETE :", str(data['tete'])],
        ["Type :", data['type'], "FUN VIS (s/qt) :", str(data['fun_vis']), "PIED :", str(data['pied'])]
    ]
    
    header_table = Table(header_data, colWidths=[3*cm, 4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('SPAN', (4,2), (5,2)),
        ('SPAN', (4,3), (5,3)),
        ('SPAN', (4,4), (5,4)),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Main Table
    table_header = [
        ["Log", "N°", "INDICES", "Indir.", "Fissures", "Pandaçage", 
         "Calcimétrie", "Age", "DESCRIPTION LITHOLOGIQUE & OBSERVATIONS"]
    ]
    
    table_data = [table_header[0]]
    for depth in data['depths']:
        row = [
            str(depth['cote']),
            depth['n'],
            depth['indices'],
            depth['indir'],
            depth['fissures'],
            depth['pandacage'],
            depth['calcimetrie'],
            depth['age'],
            depth['description']
        ]
        table_data.append(row)
    
    main_table = Table(table_data, colWidths=[1.5*cm, 0.8*cm, 1.2*cm, 1*cm, 1.5*cm, 
                                           1.5*cm, 1.5*cm, 1*cm, 6*cm])
    main_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ]))
    
    story.append(main_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Description Section
    desc = [
        Paragraph(f"<b>ORDOVICIEN Unité VI-2</b>", styles['header']),
        Paragraph(f"De {data['tete']}m - {data['pied']}m :", styles['normal']),
        Paragraph(data['litho_description'], styles['normal']),
        Paragraph(f"Porosité visuelle: {data['porosite']}", styles['normal']),
        Paragraph(f"Fluorescence directe: {data['fluorescence']}", styles['normal']),
        Paragraph("NB: Description faite à partir d'échantillons pris au bout de chaque mètre.", styles['normal'])
    ]
    
    story.extend(desc)
    
    # Footer
    footer = Paragraph(f"Fiche établie par : {data['auteur']}", styles['header'])
    story.append(Spacer(1, 1*cm))
    story.append(footer)
    
    doc.build(story)


class CoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fiche à Carotte Generator")
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ('Puits:', 'puits'),
            ('Sigle:', 'sigle'),
            ('Permis:', 'permis'),
            ('Bloc:', 'bloc'),
            ('Carottier:', 'carottier'),
            ('Type de Boue:', 'type_boue'),
            ('Carotte N°:', 'carotte_num'),
            ('Couronne:', 'couronne'),
            ('D:', 'd'),
            ('TETE (m):', 'tete'),
            ('Type:', 'type'),
            ('FUN VIS (s/qt):', 'fun_vis'),
            ('PIED (m):', 'pied'),
            ('Date Extraction (dd/mm/yyyy):', 'date_extraction'),
            ('Porosité:', 'porosite'),
            ('Fluorescence:', 'fluorescence'),
            ('Auteur:', 'auteur')
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            row = i // 3
            col = (i % 3) * 2
            ttk.Label(main_frame, text=label).grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
            entry = ttk.Entry(main_frame, width=20)
            entry.grid(row=row, column=col+1, sticky=tk.EW, padx=5, pady=2)
            self.entries[key] = entry
            
        # Litho Description
        ttk.Label(main_frame, text="Description Lithologique:").grid(row=10, column=0, columnspan=6, sticky=tk.W)
        self.litho_desc = tk.Text(main_frame, height=5, width=80)
        self.litho_desc.grid(row=11, column=0, columnspan=6, sticky=tk.EW)
        
        # Generate Button
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=12, column=0, columnspan=6, pady=20)
        ttk.Button(btn_frame, text="Generate PDF", command=self.generate_pdf).pack()
    
    def generate_pdf(self):
        data = {
            'puits': self.entries['puits'].get(),
            'sigle': self.entries['sigle'].get(),
            'permis': self.entries['permis'].get(),
            'bloc': self.entries['bloc'].get(),
            'carottier': self.entries['carottier'].get(),
            'type_boue': self.entries['type_boue'].get(),
            'carotte_num': self.entries['carotte_num'].get(),
            'couronne': self.entries['couronne'].get(),
            'd': self.entries['d'].get(),
            'tete': int(self.entries['tete'].get()),
            'type': self.entries['type'].get(),
            'fun_vis': int(self.entries['fun_vis'].get()),
            'pied': int(self.entries['pied'].get()),
            'date_extraction': datetime.strptime(self.entries['date_extraction'].get(), "%d/%m/%Y"),
            'depths': [{
                'cote': 2930,  # Add proper depth input handling
                'n': '',
                'indices': '',
                'indir': '',
                'fissures': '',
                'pandacage': '',
                'calcimetrie': '',
                'age': '25',
                'description': self.litho_desc.get("1.0", tk.END).strip()
            }],
            'litho_description': self.litho_desc.get("1.0", tk.END).strip(),
            'porosite': self.entries['porosite'].get(),
            'fluorescence': self.entries['fluorescence'].get(),
            'auteur': self.entries['auteur'].get()
        }
        
        filename = f"Fiche_{data['sigle']}_Core_{data['carotte_num']}.pdf"
        create_core_document(filename, data)
        tk.messagebox.showinfo("Success", f"PDF generated: {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoreApp(root)
    root.mainloop()

