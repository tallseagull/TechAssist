import string
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak
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
    fontSize=14,
    alignment=TA_RIGHT,
    spaceAfter=0.2,
)

def _reverse_hebrew_text(s):
    """
    Smart reverse of hebrew text
    :param s:
    :return:
    """
    nums_stack = ""
    res = ""
    for l in s[::-1]:
        if l.isdigit():
            nums_stack += l
            continue
        if l in string.ascii_letters:
            nums_stack += l
            continue
        if len(nums_stack) > 0:
            # First print the numbers from the first to the last, i.e. reverse order:
            res += nums_stack[::-1]
            nums_stack = ""
        res += l
    if len(nums_stack) > 0:
        res += nums_stack[::-1]
    return res

def _gen_crossword_table(df, is_solution=False):
    """
    Generate a table in the PDF with the data from the grid. If this is the solution data, make the letters larger and centered
    :return:
    """
    # Define cell dimensions and style
    cell_width = 30
    cell_height = 30
    cell_style = getSampleStyleSheet()['Normal']
    if is_solution:
        cell_style.fontName = "Hebrew"
        cell_style.fontSize = 14
        cell_style.alignment = TA_CENTER
    else:
        cell_style.fontSize = 8
        cell_style.alignment = TA_RIGHT

    # Define a table to hold the crossword grid
    data = []
    black_cells = []
    for i, row in enumerate(df.iterrows()):
        row_data = []
        for k, cell in enumerate(row[1]):
            if cell == '*':
                cell_content = ''
                black_cells.append((k, i))
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
    for i, k in black_cells:
        cw_tab_style.add('BACKGROUND', (i, k), (i, k), colors.gray)

    crossword_table.setStyle(cw_tab_style)
    return crossword_table

def _gen_definitions_legend(across, down):
    """
    Add a table with the across and down definitions side by side
    :param across: A list of across definitions. Each definition a string, e.g. "2. Definition for cells".
        The first item in the 'across' list is the label to use for the across (e.g. across[0] = 'Across')
    :param down: Like across, only for down
    :return:
    """
    legend_data = [
            [Paragraph(
                f"<br/><strong><u>{across[0][::-1]}</u></strong><br/>" + "<br/>".join(
                    [_reverse_hebrew_text(a) for a in across[1:]]),
                heb_style)],
            [Paragraph(
                f"<br/><strong><u>{down[0][::-1]}</u></strong><br/>" + "<br/>".join(
                    [_reverse_hebrew_text(a) for a in down[1:]]),
                heb_style)]
    ]
    table = Table(legend_data, colWidths=[90*mm, 90*mm])
    return table

# Function to create a crossword puzzle PDF
def create_crossword_pdf(df, across, down, output_filename, solved_df=None):
    """
    Crete a PDF with the crossword
    :param df: The dataframe with the grid for the puzzle. Black cells should contain the '*' char. Empty should be empty. Numbers
        (of across or down definition cells) should contain the number as string.
    :param across: A list of across definitions. Each definition a string, e.g. "2. Definition for cells".
        The first item in the 'across' list is the label to use for the across (e.g. across[0] = 'Across')
    :param down: Like across, only for down
    :param output_filename: The name of the PDF to save
    :param solved_df: (optional) the solved dataframe. If not None, added as a second page
    :return:
    """
    # Create a PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=A4)

    # Create a list to hold the content for the PDF
    elements = []

    crossword_table = _gen_crossword_table(df)
    elements.append(crossword_table)
    elements.append(Spacer(1, 20))  # Spacer for separation

    # Add across and down definitions
    legend = _gen_definitions_legend(across, down)
    elements.append(legend)

    # If we have the solution grid, add it as well with a page break:
    if solved_df is not None:
        elements.append(PageBreak())
        solution_table = _gen_crossword_table(solved_df, is_solution=True)
        elements.append(solution_table)

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
    across_definitions = ["Across", "1. Across definition 1.", "2. Across definition 2."]
    down_definitions = ["Down", "3. Down definition 1.", "*.* Down definition 2."]

    # Create a DataFrame from the crossword data
    df = pd.DataFrame.from_dict(crossword_data)

    # Output PDF file name
    output_filename = "crossword.pdf"

    # Call the function to generate the crossword PDF
    create_crossword_pdf(df, across_definitions, down_definitions, output_filename)

    print("Crossword PDF created successfully.")
