import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import declarative_base, relationship

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./stories.db"

Base = declarative_base()


# Database models
class StoryDB(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    image_bytes = Column(LargeBinary)

    questions = relationship("QuestionDB", back_populates="story")


class QuestionDB(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    question_type = Column(String)  # 'multiple_choice', 'yes_no', 'open'
    answers = Column(JSON)  # Structure varies by question type
    correct_answer = Column(Text)
    story_id = Column(Integer, ForeignKey("stories.id"))

    story = relationship("StoryDB", back_populates="questions")

# Pydantic schemas
class QuestionType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    OPEN = "open"

class Question(BaseModel):
    question: str
    type: QuestionType
    options: list[str] | None = None
    correct_answer: str | None = None

    @staticmethod
    def from_db(db_question: QuestionDB) -> 'Question':
        return Question(
            question=db_question.question_text,
            type=QuestionType(db_question.question_type),
            options=db_question.answers if db_question.question_type == 'multiple_choice' else None,
            correct_answer=db_question.correct_answer
        )

    def to_db(self, story_id: int) -> QuestionDB:
        return QuestionDB(
            question_text=self.question,
            question_type=self.type.value,
            answers=self.options if self.type == QuestionType.MULTIPLE_CHOICE else None,
            correct_answer=self.correct_answer,
            story_id=story_id
        )

class Story(BaseModel):
    id: int | None = None
    title: str | None = None
    content: str | None = None
    created_at: datetime.datetime | None = None
    image_bytes: bytes | None = None
    questions: list[Question] = []

    @staticmethod
    def from_db(db_story: StoryDB) -> 'Story':
        return Story(
            id=db_story.id,
            title=db_story.title,
            content=db_story.content,
            created_at=db_story.created_at,
            image_bytes=db_story.image_bytes,
            questions=[Question.from_db(q) for q in db_story.questions]
        )

    def to_db(self) -> StoryDB:
        return StoryDB(
            id=self.id,
            title=self.title,
            content=self.content,
            created_at=self.created_at,
            image_bytes=self.image_bytes,
            questions=[q.to_db(self.id) for q in self.questions]
        )


def create_database():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine, checkfirst=True)
    return engine