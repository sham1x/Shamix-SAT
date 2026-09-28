from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint, Float
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    streak_current = Column(Integer, default=0, nullable=False)
    streak_best = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(String(10), nullable=True) # YYYY-MM-DD UTC
    target_test_date = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    progress_records = relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    attempts = relationship("HomeworkAttempt", back_populates="user", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="user", cascade="all, delete-orphan")
    user_badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    xp_events = relationship("XPEvent", back_populates="user", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String(50), primary_key=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(50), nullable=False) # math | reading_writing
    module = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    video_url = Column(String(500), nullable=False)
    duration_sec = Column(Integer, default=0)
    duration_str = Column(String(20), default="15 mins")
    order = Column(Integer, default=0)
    materials = Column(JSON, nullable=True) # keyTakeaways, transcript, etc.

    homeworks = relationship("Homework", back_populates="lesson")

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(String(50), ForeignKey("lessons.id"), nullable=False)
    watched_seconds = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="progress_records")

class Homework(Base):
    __tablename__ = "homework"

    id = Column(String(50), primary_key=True)
    lesson_id = Column(String(50), ForeignKey("lessons.id"), nullable=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(50), nullable=False)
    skill = Column(String(100), nullable=False)
    due_date = Column(String(10), nullable=False) # YYYY-MM-DD
    xp_reward = Column(Integer, default=150)
    est_time = Column(String(20), default="12 mins")

    lesson = relationship("Lesson", back_populates="homeworks")
    questions = relationship("Question", back_populates="homework", cascade="all, delete-orphan")
    attempts = relationship("HomeworkAttempt", back_populates="homework", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    homework_id = Column(String(50), ForeignKey("homework.id"), nullable=False)
    stem = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # List[str]
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    topic = Column(String(100), nullable=False)
    difficulty = Column(String(20), default="Medium")

    homework = relationship("Homework", back_populates="questions")

class HomeworkAttempt(Base):
    __tablename__ = "homework_attempts"
    __table_args__ = (UniqueConstraint("user_id", "homework_id", name="uq_user_homework_attempt"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    homework_id = Column(String(50), ForeignKey("homework.id"), nullable=False)
    status = Column(String(20), default="in_progress") # in_progress | completed
    current_question = Column(Integer, default=0)
    score = Column(String(10), nullable=True) # e.g. "100%"
    started_at = Column(DateTime(timezone=True), default=utc_now)
    submitted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="attempts")
    homework = relationship("Homework", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")

class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    __table_args__ = (UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),)

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("homework_attempts.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    attempt = relationship("HomeworkAttempt", back_populates="answers")

class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    date = Column(String(10), nullable=False) # YYYY-MM-DD
    day_num = Column(Integer, nullable=False)
    time = Column(String(50), nullable=False)
    instructor = Column(String(100), nullable=False)
    subject = Column(String(50), default="SAT Prep")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("user_id", "check_date", "session_id", name="uq_user_date_session"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True)
    check_date = Column(String(10), nullable=False) # YYYY-MM-DD
    status = Column(String(20), nullable=False, default="present") # present | absent | late | excused
    checked_in_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="attendance_records")

class Badge(Base):
    __tablename__ = "badges"

    id = Column(String(50), primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(100), nullable=False)
    criteria = Column(JSON, nullable=True)

    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(String(50), ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")

class XPEvent(Base):
    __tablename__ = "xp_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    reason = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="xp_events")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String(50), primary_key=True)
    deck = Column(String(50), default="default")
    category = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
