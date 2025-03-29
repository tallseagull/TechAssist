import streamlit as st
from sqlfluff.dialects.dialect_soql import DateLiteralNSegment

from backend.database.models import Story
from backend.text_generator import TextAndQuestionsGenerator
from backend.database.crud import DatabaseManager
from backend.docx_generator import DocxGenerator
from PIL import Image
from io import BytesIO
import tempfile


st.set_page_config(layout="wide")


def display_story_results(story: Story, docx_gen: DocxGenerator):
    
    # Display story content and image side by side if image is not None
    if story.image_bytes:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(story.title)
            st.write(story.content)
        with col2:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(story.image_bytes)
                tmp_file_path = tmp_file.name

                image = Image.open(tmp_file_path)
                target_height = 400
                if image.height > target_height:
                    image.thumbnail((image.width, target_height))
                st.image(image, caption="Generated Image", use_column_width=True)
    else:
        st.subheader(story.title)
        st.write(story.content)

    st.subheader("Questions")
    for q in story.questions:
        if q.type == "multiple_choice":
            st.write(f"**Question:** {q.question}")
            for option in q.options:
                st.write(f"- {option}")
        elif q.type == "yes_no":
            st.write(f"**Question:** {q.question}")
            st.write(f"- Yes")
            st.write(f"- No")
        elif q.type == "open":
            st.write(f"**Question:** {q.question}")
            st.write("---")

    # Generate and provide download button for DOCX
    docx_path = docx_gen.generate(story)
    with open(docx_path, "rb") as file:
        st.download_button(
            label="Download DOCX",
            data=file,
            file_name="story.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

def main():
    st.title("EFL Reading Comprehension Helper")

    # Initialize backend components and store in session
    if "db" not in st.session_state:
        st.session_state.db = DatabaseManager()
    if "text_gen" not in st.session_state:
        st.session_state.text_gen = TextAndQuestionsGenerator()
    if "docx_gen" not in st.session_state:
        st.session_state.docx_gen = DocxGenerator()

    db = st.session_state.db
    text_gen = st.session_state.text_gen
    docx_gen = st.session_state.docx_gen

    # Sidebar with saved stories
    with st.sidebar:
        st.header("Saved Stories")
        stories = db.list_stories()
        title_to_id = {"**New Story**": None}  # Initialize with a placeholder for new story
        
        for s in stories:
            title = s["title"]
            if title in title_to_id:
                count = 1
                new_title = f"{title}-{count}"
                while new_title in title_to_id:
                    count += 1
                    new_title = f"{title}-{count}"
                title_to_id[new_title] = s["id"]
            else:
                title_to_id[title] = s["id"]
        
        selected_story_title = st.radio("Choose a story", list(title_to_id.keys()), index=None)


    # Main interface
    if (selected_story_title is None) or (selected_story_title == "New Story"):
        st.session_state.generated_story_id = None
        st.session_state.current_story = None

        theme = st.text_input("Enter story theme/title:")
        with open("vocab.txt", "r") as file:
            vocab_txt = file.read().strip()
            vocabulary = [v.strip() for v in vocab_txt.split(",")]

        if st.button("Generate Story"):
            request = {"topic": theme, "vocabulary": ', '.join(vocabulary)}

            with st.spinner("Generating story..."):
                generated_story = text_gen.invoke(request)

                # Save to DB
                db.add_story(generated_story)

                # Display results
                st.session_state.current_story = generated_story  # Save the generated story to session state
                display_story_results(generated_story, docx_gen)

                # Save generated story ID to session state
                st.session_state.current_story = generated_story
    else:
        # If a story is selected from the sidebar, display it
        if selected_story_title:
            selected_story_id = title_to_id[selected_story_title]
            story = db.get_story_by_id(selected_story_id)
            st.session_state.current_story = story  # Save the story to session state
            display_story_results(story, docx_gen)
        elif st.session_state.current_story:
            # If no story is selected but one exists in session state, display it
            story = st.session_state.current_story
            display_story_results(story, docx_gen)



if __name__ == "__main__":
    main()
