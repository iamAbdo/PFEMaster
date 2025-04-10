from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from tkinter import filedialog

def export_pdf(app):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    pdf = pdf_canvas.Canvas(file_path, pagesize=A4)
    a4_width, a4_height = A4
    margin = 40
    line_height = 14
    cell_height = 20
    cell_width = 60

    for page in app.pages:
        pdf.setFont("Helvetica", 12)
        y_position = a4_height - margin
        
        for col_num, text_widget in enumerate(page):
            # Get all text with tags
            content = text_widget.get("1.0", "end-1c")
            
            # Get bold ranges
            bold_ranges = []
            start_idx = "1.0"
            while True:
                range_start = text_widget.tag_nextrange("bold", start_idx)
                if not range_start:
                    break
                bold_ranges.append((
                    text_widget.count("1.0", range_start[0], "chars")[0],
                    text_widget.count("1.0", range_start[1], "chars")[0]
                ))
                start_idx = range_start[1]
            
            # Calculate column positions
            x = margin + sum(app.column_pixel_widths[:col_num])
            
            # Split text into lines
            lines = content.split('\n')
            for line in lines:
                if y_position < margin:
                    pdf.showPage()
                    y_position = a4_height - margin
                    pdf.setFont("Helvetica", 12)
                
                # Draw text with bold formatting
                char_pos = 0
                while char_pos < len(line):
                    # Check if current position is in bold range
                    in_bold = any(start <= char_pos < end for (start, end) in bold_ranges)
                    
                    if in_bold:
                        pdf.setFont("Helvetica-Bold", 12)
                        # Find maximum bold range
                        bold_end = min([end for (start, end) in bold_ranges if start <= char_pos < end])
                        chunk = line[char_pos:bold_end]
                    else:
                        pdf.setFont("Helvetica", 12)
                        chunk = line[char_pos:]
                        if bold_ranges:
                            next_bold = min([start for (start, end) in bold_ranges if start > char_pos])
                            chunk = line[char_pos:next_bold]
                    
                    pdf.drawString(x, y_position, chunk)
                    char_pos += len(chunk)
                
                y_position -= line_height
                
        pdf.showPage()

    pdf.save()
