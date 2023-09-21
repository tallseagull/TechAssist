import streamlit as st
from Math.math_worksheet import generate_math_worksheet, DIR_HORIZONTAL, DIR_VERTICAL

st.title("Math Worksheets")
worksheet_title = st.text_input("Worksheet name:", "משימה בחשבון", key="sheet_title")
operation_type = st.radio(
        "Operation type:",
        key="op_type",
        options=["plus", "minus", "times"])
max_number_range = st.number_input("Max number", min_value=5, max_value=1000, step=5, value=100)  # Choose from '10', '100', '1000'
horizontal_or_vertical = st.radio("Horizontal or Vertical?", key="horiz_vert", options=["Horizontal", "Vertical"])
num_questions = st.number_input("Number of questions", min_value=30, max_value=100, step=10)  # Number of questions per page
output_pdf = '/tmp/math_worksheet.pdf'

def _create_worksheet():
    direction = DIR_HORIZONTAL if horizontal_or_vertical=="Horizontal" else DIR_VERTICAL
    generate_math_worksheet(worksheet_title, operation_type, max_number_range, num_questions, output_pdf, direction)
    print(f'PDF created: {output_pdf}')

_create_worksheet()

with open(output_pdf, "rb") as fp:
    st.download_button("Download", data=fp, file_name="math_worksheet.pdf", on_click=_create_worksheet)