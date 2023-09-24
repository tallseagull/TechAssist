from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import colors
import pandas as pd
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

pdfmetrics.registerFont(TTFont('Hebrew', '/Users/talsegalov/code/TechAssist/fonts/arial-hebrew.ttf'))

heb_style = ParagraphStyle(
    name='CustomStyle',
    fontName='Hebrew',
    fontSize=16,
    alignment=TA_CENTER,
)

# Function to create a crossword puzzle PDF
def create_crossword_pdf(df, across, down, output_filename):
    # Create a PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)

    # Create a list to hold the content for the PDF
    elements = []

    # Define cell dimensions and style
    cell_width = 30
    cell_height = 30
    cell_style = getSampleStyleSheet()['Normal']
    cell_style.fontSize = 8
    cell_style.alignment = TA_RIGHT

    # Define a table to hold the crossword grid
    data = []
    black_cells = []
    for i,row in enumerate(df.iterrows()):
        row_data = []
        for k,cell in enumerate(row[1]):
            if cell == '*':
                cell_content = '*'
                black_cells.append((i, k))
            elif cell == ' ':
                cell_content = ''
            else:
                cell_content = cell
            row_data.append(Paragraph(cell_content, cell_style))
        data.append(row_data)

    # Create the crossword table
    crossword_table = Table(data, colWidths=cell_width, rowHeights=cell_height)
    cw_tab_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])
    # for i,k in black_cells:
    #     cw_tab_style.add('BACKGROUND', (i,k), (i,k), colors.black)

    crossword_table.setStyle(cw_tab_style)

    elements.append(crossword_table)
    elements.append(Spacer(1, 20))  # Spacer for separation

    # Add across and down definitions
    style = ParagraphStyle(name='Normal')
    style.leading = 16
    elements.append(Paragraph("<strong>Across:</strong><br/>" + across, heb_style))
    elements.append(Spacer(1, 20))  # Spacer for separation
    elements.append(Paragraph("<strong>Down:</strong><br/>" + down, heb_style))

    # Build the PDF document
    doc.build(elements)

if __name__ == '__main__':
    # Sample crossword data
    crossword_data = {
        'A': ['1', '*', ' ', '2'],
        'B': ['*', '*', ' ', ' '],
        'C': ['3', ' ', ' ', ' '],
        'D': [' ', ' ', ' ', '*'],
    }

    # Sample definitions
    across_definitions = "1. Across definition 1.<br/>2. Across definition 2."
    down_definitions = "3. Down definition 1.<br/>*.* Down definition 2."

    # Create a DataFrame from the crossword data
    df = pd.DataFrame.from_dict(crossword_data)

    # Output PDF file name
    output_filename = "crossword.pdf"

    # Call the function to generate the crossword PDF
    create_crossword_pdf(df, across_definitions, down_definitions, output_filename)

    print("Crossword PDF created successfully.")
