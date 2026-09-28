import os

# Set a valid test SECRET_KEY in environment before importing config/app
os.environ.setdefault("SECRET_KEY", "test_secret_key_32_characters_minimum_length_safe")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import User, Homework, Question, Badge
from backend.app.security import hash_password
from backend.app.routers.auth import _rate_limit_store

# Use StaticPool so all connections to in-memory SQLite share the same database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Seed minimal test data
    demo_user = User(
        username="testdemo",
        email="testdemo@shamixprep.sat",
        password_hash=hash_password("TestDemo123!"),
        display_name="Test Demo User",
        xp=1000,
        level=3,
        streak_current=5,
        streak_best=5
    )
    session.add(demo_user)
    
    hw = Homework(
        id="testhw-1", title="Test Math Drill", subject="Math", skill="Algebra",
        due_date="2026-12-31", xp_reward=150, est_time="10 mins"
    )
    session.add(hw)
    session.flush()

    q1 = Question(
        homework_id="testhw-1", stem="What is 2 + 2?", options=["A) 3", "B) 4", "C) 5"],
        correct_index=1, explanation="2 + 2 equals 4.", topic="Basic Math", difficulty="Easy"
    )
    session.add(q1)

    badge = Badge(
        id="b1", code="night_owl", name="Night Learner 🌙", description="Complete lessons after 8 PM", icon="icon", criteria={"target": 3}
    )
    session.add(badge)

    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    _rate_limit_store.clear()
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    _rate_limit_store.clear()
