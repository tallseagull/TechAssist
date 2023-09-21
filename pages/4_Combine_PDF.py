import io
import os

from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
import streamlit as st
from tempfile import TemporaryDirectory

# Function to create a PDF page using reportlab
def create_blank_page(width, height):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.showPage()
    c.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    return new_pdf.getPage(0)

# List of PDF input files to concatenate
# input_files = ["input1.pdf", "input2.pdf", "input3.pdf"]

def combine_pdf_files(input_files, output_file):
    # Create a PdfFileWriter object to store the output
    output_pdf = PdfWriter()

    # Iterate through the input files
    for input_file in input_files:
        input_pdf = PdfReader(open(input_file, "rb"))

        # Iterate through pages in each input file and add them to the output
        for page_num in range(len(input_pdf.pages)):
            page = input_pdf.pages[page_num]
            output_pdf.add_page(page)

    # Create a new PDF output file and write the concatenated pages
    if os.path.isfile(output_file):
        os.remove(output_file)
    with open(output_file, "wb") as fp:
        output_pdf.write(fp)

    print("PDF files concatenated successfully!")

st.title("PDF Files combiner")
st.write("Please upload all PDF files you'd like to combine below, then download the result to get the combined PDF.")

uploaded_files = st.file_uploader("Choose PDF files", accept_multiple_files=True, type="pdf")
input_files = []
with TemporaryDirectory() as td:
    for uploaded_file in uploaded_files:
        st.write("filename:", uploaded_file.name)
        input_files.append(os.path.join(td, uploaded_file.name))
        with open(input_files[-1], "wb") as fp:
            fp.write(uploaded_file.read())

    # Now combine all to one new file:
    combine_pdf_files(input_files, "/tmp/comb_pdf.pdf")

if len(input_files) > 0:
    with open("/tmp/comb_pdf.pdf", "rb") as fp:
        st.download_button("Download PDF", data=fp, file_name="combined_pdf.pdf")