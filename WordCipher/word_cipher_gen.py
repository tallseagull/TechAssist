from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.shared import Cm
import numpy as np

# Unicodes are used the "encrypt" the text we want
unicodes_list = ["\u2582", "\u25a0", "\u25c6", "\u25b6", "\u259a",
                 "\u25ce", "\u2665", "\u2663", "\u25d3", "\u25f0",
                 "\u2602", "\u273f", "\u2606", "\u2691", "\u25e1",
                 "\u2702", "\u266b", "\u26cc"]

TEXT_SIZE = 16
SQUARE_SIZE = 28
LETTER_16_WIDTH = 0.2
MARGIN_WIDTH = 0.9

def encrypt_text(solutions, secret):
    """
    Creates an encryption for the solutions and secret text, replacing each unique char with one of our unicodes:
    :param solutions: the list of strings that are the solutions
    :param secret: The secret text we want to discover last
    :return: dict with keys: {"solutions": [list of encrypted solutions], "secret": encrypted secret string, "key": key}
    """
    unique_chars = set([l for l in "".join(solutions)])
    assert all(l in unique_chars for l in secret), Exception("Not all chars in secret are in the solutions")

    # Now create a random order of the unicodes:
    unicode_ord = np.random.choice(len(unicodes_list), len(unique_chars), replace=False)
    mapping_dict = {c:k for c,k in zip(unique_chars, unicode_ord)}

    # Now "encrypt" the solutions and the secret:
    res = {"key": mapping_dict,
           "solutions": [[unicodes_list[mapping_dict[c]] for c in sol] for sol in solutions],
           "secret": [unicodes_list[mapping_dict[c]] for c in secret]}
    return res

def _set_font_size(paragraphs, font_size=20):
    for paragraph in paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(font_size)  # Set font size to 20

def _get_width(txt, font_size):
    return MARGIN_WIDTH + (len(txt) * LETTER_16_WIDTH) * font_size / 16.

# Function to create a table with 6 columns and add text in the first row
def create_table_with_columns_and_text(doc, question, ans_symbols):
    """
    Create a table in the doc to contain the question text, then the symbols for the solution beneath empty squares
    :param doc: The doc created
    :param question: The question text
    :param ans_symbols: The answer symbols as a list of chars
    :return: The table created
    """
    n_cols = len(ans_symbols) + 1

    # Add a table, aligned to the right:
    # paragraph = doc.add_paragraph()
    # paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    table = doc.add_table(rows=2, cols=n_cols)
    table.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    table.allow_autofit = True  # Disable autofit

    # Set the width of the first five columns for a single character
    for i in range(n_cols-1):
        cell = table.cell(0, i)
        cell.text = "\u25A1"
        cell.vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM  # Center align vertically
        cell.width = Cm(1)  # Adjust the width as needed
        _set_font_size(cell.paragraphs, SQUARE_SIZE)

        cell = table.cell(1, i)
        cell.width = Cm(1)  # Adjust the width as needed
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP  # Center align vertically
        cell.text = ans_symbols[i]
        _set_font_size(cell.paragraphs, TEXT_SIZE)

    # Set the width of the last column to fill the remaining space on the page
    cell = table.cell(0, n_cols-1)
    cell.width = Cm(_get_width(question, TEXT_SIZE))  # Adjust the width as needed
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER  # Center align vertically
    cell.text = question
    _set_font_size(cell.paragraphs, TEXT_SIZE)

    return table

# Function to add an empty paragraph for spacing
def add_empty_paragraph(doc):
    p = doc.add_paragraph()
    run = p.add_run("")
    run.font.size = Pt(1)  # Set font size to the smallest value for an empty line

# Your input sentences and symbols
sentences = [
    ("איזו עונה מתחילה בסוכות", "סתו"),
    ("פרח גבוה שפורח עכשיו", "חצב"),
    ("בונים אותה בחג סוכות", "סוכה"),
    ("פרי עם המון גרעינים אדומים", "רימונ"),
    ("חג סוכות נקרא גם חג", "האסיפ")
]
secret = "הכוכבימ"
secret_q = " יודעים שהתחיל החג לפי"
data = encrypt_text([s[1][::-1] for s in sentences], secret[::-1])

# Create a new Word document
doc = Document()

# Add questions with symbols to the document
for i in range(len(sentences)):
    question = sentences[i][0]
    symbols = data["solutions"][i]
    create_table_with_columns_and_text(doc, question, symbols)
    add_empty_paragraph(doc)
    # add_question_with_symbols(doc, question, symbols)

create_table_with_columns_and_text(doc, secret_q, data["secret"])

# p = doc.add_paragraph()
# p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
# run = p.add_run("".join(unicodes_list))
# run.font.size = Pt(20)

# Save the document
doc.save("/Users/talsegalov/Downloads/hebrew_questions.docx")

print(unicodes_list)

