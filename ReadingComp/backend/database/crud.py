from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.models import SQLALCHEMY_DATABASE_URL, StoryDB, QuestionDB, Story, Question, create_database


class DatabaseManager:
    def __init__(self):
        self.engine = create_database()
        #  = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def list_stories(self) -> list[dict]:
        with self.SessionLocal() as session:
            db_stories = session.query(StoryDB.id, StoryDB.title).all()
            return [{"id": db_story.id, "title": db_story.title} for db_story in db_stories]
        
    def get_story_by_id(self, story_id: int) -> Story:
        with self.SessionLocal() as session:
            db_story = session.query(StoryDB).filter(StoryDB.id == story_id).first()
            if db_story:
                return Story.from_db(db_story)
            return None

    def add_story(self, story: Story):
        with self.SessionLocal() as session:
            db_story = story.to_db()
            session.add(db_story)
            session.commit()
            session.refresh(db_story)
            
            # Add questions to the DB
            for question in story.questions:
                db_question = question.to_db(db_story.id)
                session.add(db_question)
            session.commit()     

    def delete_story_by_id(self, story_id: int) -> bool:
        with self.SessionLocal() as session:
            db_story = session.query(StoryDB).filter(StoryDB.id == story_id).first()
            if db_story:
                session.delete(db_story)
                session.commit()
                return True
            return False
