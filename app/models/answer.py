from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.sql import func
from app.database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    overall_score = Column(Float, nullable=True)
    logic_score = Column(Float, nullable=True)
    specificity_score = Column(Float, nullable=True)
    delivery_score = Column(Float, nullable=True)
    strengths = Column(Text, nullable=True)     # JSON array string
    improvements = Column(Text, nullable=True)  # JSON array string
    model_answer = Column(Text, nullable=True)
    star_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
