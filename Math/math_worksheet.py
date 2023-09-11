from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph, Table, TableStyle, Spacer, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import random

DIR_VERTICAL = 0
DIR_HORIZONTAL = 1

left_style = ParagraphStyle(
    name='CustomStyle',
    fontName='Helvetica',
    fontSize=18,
    alignment=TA_CENTER,
)

right_style = ParagraphStyle(
    name='CustomStyle',
    fontName='Helvetica',
    fontSize=18,
    alignment=TA_RIGHT,
)

def create_vertical_question(num1, operation, num2):
    paragraph = [Paragraph(f'{str(num1)}<br/>', right_style),
                 Paragraph(f'{operation}<br/>', left_style),
                 Paragraph(f'{str(num2)}<br/>----------<br/><br/><br/><br/><br/>', right_style),
                ]
    return paragraph

def generate_math_worksheet(title, operation, number_range, num_questions, output_pdf, direction=DIR_VERTICAL):
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    story = []

    # Create a title for the worksheet
    title_style = getSampleStyleSheet()['Title']
    title_text = Paragraph(title, title_style)
    story.append(title_text)

    # Define the operation symbol and operator function
    if operation == 'plus':
        symbol = '+'
        operator = lambda x, y: x + y
    elif operation == 'minus':
        symbol = '-'
        operator = lambda x, y: x - y
    elif operation == 'times':
        symbol = '×'
        operator = lambda x, y: x * y
    else:
        raise ValueError(f"Unknown symbol")

    table_data = []
    ncols = 3
    for _ in range(num_questions // ncols):
        row_data = []
        for _ in range(ncols):
            num1 = random.randint(1, number_range)
            num2 = random.randint(1, number_range)

            # Create the question in the row:
            row_data.append(create_vertical_question(num1, symbol, num2))
        table_data.append(row_data)

    table = Table(table_data, colWidths=[150, 150, 150])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 18),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    doc.build(story)

if __name__ == "__main__":
    # User-defined options
    worksheet_title = "Math Worksheet Example"
    operation_type = "plus"  # Can be 'plus', 'minus', or 'times'
    max_number_range = 1000  # Choose from '10', '100', '1000'
    num_questions = 20  # Number of questions per page
    output_pdf = '/Users/talsegalov/Downloads/math_worksheet.pdf'

    generate_math_worksheet(worksheet_title, operation_type, max_number_range, num_questions, output_pdf)
    print(f'PDF created: {output_pdf}')
