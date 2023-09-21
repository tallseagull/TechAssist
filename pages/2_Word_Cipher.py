import streamlit as st
from WordCipher.word_cipher_gen import WordCipherGen

st.title("שאלות")
q_cols = st.columns([0.3, 0.7])
with q_cols[1]:
    st.write("שאלה")
    questions = [st.text_input("", key=f"q{i}") for i in range(6)]

with q_cols[0]:
    st.write("תשובה")
    answers = [st.text_input("", key=f"a{i}") for i in range(6)]

st.title("הסוד")
s_cols = st.columns([0.3, 0.7])
with s_cols[1]:
    st.write("השאלה לסוד")
    secret_q = st.text_input("", key="sq")

with s_cols[0]:
    st.write("התשובה")
    secret_ans = st.text_input("", key="si")

if st.button("Go!"):
    sentences = [(questions[i], answers[i]) for i in range(len(questions)) if (questions[i] is not None) and (len(questions[i]) > 0)]
    secret = (secret_q, secret_ans)

    word_cipher = WordCipherGen()
    word_cipher.create_doc(sentences, secret)
    word_cipher.save_doc("/tmp/worksheet.docx")

    with open("/tmp/worksheet.docx", "rb") as fp:
        st.download_button("Download", data=fp, file_name="worksheet.docx")
