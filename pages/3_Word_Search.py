import os

from word_search_generator import WordSearch
import streamlit as st

st.title("Wordsearch Generator")
word_list = st.text_area("Words to use (comma separated):")
# word_list = [wrd.strip().upper() for wrd in word_list_field.split(',')]

puzzle_size = st.number_input("Puzzle size", 15, 35, 20)

# Create the puzzle:
if st.button("Go") and (len(word_list) > 0):
    puzzle = WordSearch(word_list)
    puzzle.size = puzzle_size
    os.remove("/tmp/puzzle.pdf")
    puzzle.save(path="/tmp/puzzle.pdf")

    with open("/tmp/puzzle.pdf", "rb") as fp:
        st.download_button("Download result", data=fp, file_name="puzzle.pdf")
