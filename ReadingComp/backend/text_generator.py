import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from typing import Dict, List, Annotated, Optional
import json
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.api_core.exceptions import NotFound

from backend.image_gen import generate_sketch_cartoon
from backend.prompts import TEXT_GENERATION_PROMPT, TEXT_STYLE_PROMPT, QUESTIONS_PROMPT, IMAGE_PROMPT
from backend.database.models import Story, Question, SQLALCHEMY_DATABASE_URL


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")


def clean_json(json_text):
    json_text = json_text.strip()
    json_text = json_text.replace('```json', '').replace('```', '')
    return json_text


class GraphState(BaseModel):
    topic: Annotated[str, Field(description="The requested text topic")]
    vocabulary: Annotated[str, Field(description="The comma separated list of vocabulary words")]
    text: Annotated[str, Field(description="The generated text.", default="")]
    questions: Annotated[List[Dict], Field(description="Generated questions about the text.", default_factory=list)]
    title: Annotated[str, Field(description="The title of the text.", default="")]
    image_bytes: Annotated[Optional[bytes], Field(description="The bytes of a PNG image", default=None)]


class TextAndQuestionsGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", google_api_key=GOOGLE_API_KEY)
        self.workflow = self.build_langgraph()

    def build_langgraph(self):
        text_generation_prompt = ChatPromptTemplate.from_template(
            """
            {TEXT_GENERATION_PROMPT}

            WRITING STYLE: {TEXT_STYLE_PROMPT}

            VOCABULARY: {vocabulary}.

            TOPIC: {topic}.
            """
        )

        question_generation_prompt = ChatPromptTemplate.from_template(
            """
            {QUESTIONS_PROMPT}

            TEXT: {text}
            """
        )

        title_generation_prompt = ChatPromptTemplate.from_template(
            """
            You are an expert in creating English language learning materials for beginner to lower-intermediate students. 
            Your task is to create an engaging title for the following text:

            {text}

            The title must be short and engaging. In your output provide only the title text, no other information.
            The title should be no longer than 5 words.
            """
        )

        def generate_text(state: GraphState):
            result = self.llm.invoke(text_generation_prompt.format_messages(TEXT_GENERATION_PROMPT=TEXT_GENERATION_PROMPT, 
                                                                            TEXT_STYLE_PROMPT=TEXT_STYLE_PROMPT, 
                                                                            topic=state.topic,
                                                                            vocabulary=state.vocabulary))
            return {"text": result.content}

        def generate_questions(state: GraphState):
            result = self.llm.invoke(question_generation_prompt.format_messages(QUESTIONS_PROMPT=QUESTIONS_PROMPT, text=state.text))
            questions = json.loads(clean_json(result.content))
            return {"questions": questions}

        def generate_title(state: GraphState):
            result = self.llm.invoke(title_generation_prompt.format_messages(text=state.text))
            return {"title": result.content}
            

        def generate_image(state: GraphState):
            image_bytes = generate_sketch_cartoon(story_content=state.text)
            return {"image_bytes": image_bytes}
        

        workflow = StateGraph(GraphState)
        workflow.add_node("generate_text", generate_text)
        workflow.add_node("generate_questions", generate_questions)
        workflow.add_node("generate_title", generate_title)
        workflow.add_node("generate_image", generate_image)

        workflow.add_edge("generate_text", "generate_title")
        workflow.add_edge("generate_title", "generate_questions")
        workflow.add_edge("generate_questions", "generate_image")
        workflow.add_edge("generate_image", END)

        workflow.set_entry_point("generate_text")
        return workflow.compile()

    def invoke(self, request: dict) -> Story:
        res = self.workflow.invoke(request)

        # Create the Story object:
        story_data = res.get("text")
        questions_data = res.get("questions")
        title = res.get("title")
        image_bytes = res.get("image_bytes")
        story = Story(title=title, content=story_data, questions=[Question(**q) for q in questions_data], image_bytes=image_bytes)
        return story
        
    
    def save_to_db(self, state: GraphState):
        """
        Save the result to the DB
        """
        # Create a session
        engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Use the with session syntax
        with SessionLocal() as session:
            # Convert state response to Story and Questions
            story_data = state.get("text")
            questions_data = state.get("questions")
            story = Story(title=state.get("title"), 
                          content=story_data, 
                          questions=[Question(**q) for q in questions_data],
                          image_bytes=state.image_bytes)

            # Create DB equivalents
            db_story = story.to_db()
            session.add(db_story)
            session.commit()
            
            # Add questions to the DB
            for question in story.questions:
                db_question = question.to_db(db_story.id)
                session.add(db_question)
            session.commit()
