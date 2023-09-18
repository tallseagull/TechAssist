from word_search_generator import WordSearch
import streamlit as st

st.title("Wordsearch Generator")
word_list = st.text_area("Words to use (comma separated):")
# word_list = [wrd.strip().upper() for wrd in word_list_field.split(',')]

puzzle_size = st.number_input("Puzzle size", 15, 35, 20)

# Create the puzzle:
puzzle = WordSearch(word_list)
puzzle.size = puzzle_size
puzzle.save(path="/tmp/puzzle.pdf")

st.download_button("Download result", file_name="/tmp/puzzle.pdf")
