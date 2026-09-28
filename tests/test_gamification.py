from datetime import datetime, timezone, timedelta
from backend.app.services.gamification import calculate_level, update_streak, award_xp
from backend.app.models import User

def test_level_calculation():
    assert calculate_level(0) == 1
    assert calculate_level(499) == 1
    assert calculate_level(500) == 2
    assert calculate_level(1499) == 3
    assert calculate_level(3450) == 7

def test_streak_and_xp_award(db_session):
    user = db_session.query(User).filter(User.username == "testdemo").first()
    initial_xp = user.xp

    award_xp(db_session, user, 200, "test_reason")
    db_session.commit()

    assert user.xp == initial_xp + 200
    assert user.level == calculate_level(user.xp)

def test_streak_reset_after_skipped_day(db_session):
    user = db_session.query(User).filter(User.username == "testdemo").first()
    user.streak_current = 5
    user.streak_best = 5
    # Set last activity date to 2 days ago
    two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
    user.last_activity_date = two_days_ago
    db_session.flush()

    res = update_streak(db_session, user)
    assert res is True
    assert user.streak_current == 1
    assert user.streak_best == 5 # Best streak is retained
