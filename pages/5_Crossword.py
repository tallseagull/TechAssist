import os
import string

import streamlit as st
from crossword_gen.crossword_gen import Crossword, read_word_and_defs
from crossword_gen.cw_to_pdf import create_crossword_pdf

st.title("Crossword Puzzle Generator")
"""
This tool creates a crossword puzzle. You need to do the following to create one:
1. Select size (it will be at most the size you selected). Size is the number of rows and columns in the result.
2. Select the target words file. The file should be a text file with one definition per row. Each row looks like: answer | question. (you can download the example file)
3. Select extra-words file - these are extra, general definitions to add to the puzzle. Only some of these will be used, if they fit.
4. Create the puzzle, then download the result!
"""

heb_defs_data = """סוכה | יושבים בה בחג סוכות
רימון | פרי עם המון גרעינים
שופר | משמיע תרועה בראש השנה
תשפד | השנה שהתחילה עכשיו
תפוח | אוכלים אותו עם דבש
שנהטובה | ברכה לשנה החדשה
יורה | הגשם הראשון של השנה
תשרי | החודש הראשון בשנה העברית
אופניים | יש להם שני גלגלים ונוסעים עליהם
כוכבים | נקודות של אור בשמיים"""

cw_size = st.number_input("Crossword size", 10, 20)
cols = st.columns(2)
cw_words_data = cols[0].file_uploader("Word definitions")
cols[0].download_button("Download sample word definitions", file_name="sample_defs.txt", data=heb_defs_data)
cw_extra_words_data = cols[1].file_uploader("Extra word definitions")
is_hebrew = st.toggle("Is Hebrew?", value=True)

word_list = None
if cw_words_data is not None:
    data = cw_words_data.read().decode("utf-8")
    word_list = read_word_and_defs(data=data, hebrew=is_hebrew)

if cw_extra_words_data is not None:
    data = cw_extra_words_data.read().decode("utf-8")
    extra_word_list = read_word_and_defs(data=data, hebrew=is_hebrew)
else:
    extra_word_list = []

if is_hebrew:
    letters = 'אבגדהוזחטיכלמנסעפצקרשת'
else:
    letters = string.ascii_lowercase

if (word_list is not None) and st.button("Go!"):
    crossword = Crossword(10, 10, '*', 5000, word_list, extra_words=extra_word_list, letters=letters, rtl=True)
    crossword.compute_crossword(time_permitted=5.00, spins=2)
    print(len(crossword.current_word_list), 'out of', len(word_list))

    # Create the PDF:
    # Create a DataFrame from the crossword data
    empty_df, solved_df = crossword.display()

    # Sample definitions
    across_defs, down_defs = crossword.legend()
    across_definitions = ["אופקי"] + across_defs
    down_definitions = ["מאונך"] + down_defs

    # Output PDF file name
    output_filename = "/tmp/crossword.pdf"

    # Call the function to generate the crossword PDF
    if os.path.isfile(output_filename):
        os.remove(output_filename)
    create_crossword_pdf(empty_df, across_definitions, down_definitions, output_filename, solved_df=solved_df)

    with open(output_filename, "rb") as fp:
        st.download_button("Download result", data=fp, file_name="crossword.pdf")