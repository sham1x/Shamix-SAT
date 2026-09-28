from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models import User, XPEvent, Badge, UserBadge, HomeworkAttempt, AttendanceRecord

def get_utc_today_str() -> str:
    """Returns UTC date string YYYY-MM-DD."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

DEFAULT_TARGET_DATE = (datetime.now(timezone.utc) + timedelta(days=60)).strftime("%Y-%m-%dT18:00:00")

def calculate_level(xp: int) -> int:
    """Formula: Level 1 starts at 0 XP. Every 500 XP grants 1 level."""
    return max(1, int(xp / 500) + 1)

def award_xp(db: Session, user: User, amount: int, reason: str) -> XPEvent:
    """
    Grants XP to user, creates XPEvent log, calculates level, and triggers badge evaluation.
    """
    event = XPEvent(user_id=user.id, amount=amount, reason=reason)
    db.add(event)
    
    user.xp += amount
    user.level = calculate_level(user.xp)
    db.flush()

    evaluate_badges(db, user)
    return event

def update_streak(db: Session, user: User) -> bool:
    """
    Evaluates user daily streak based on UTC dates.
    Increases streak by 1 on the first activity of a new calendar day.
    Resets to 1 if one or more calendar days were skipped.
    Returns True if streak updated.
    """
    today_str = get_utc_today_str()
    if user.last_activity_date == today_str:
        return False # Already logged activity today

    if not user.last_activity_date:
        user.streak_current = 1
    else:
        try:
            last_dt = datetime.strptime(user.last_activity_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            today_dt = datetime.strptime(today_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            delta_days = (today_dt - last_dt).days

            if delta_days == 1:
                user.streak_current += 1
            elif delta_days > 1:
                user.streak_current = 1
        except Exception:
            user.streak_current = 1

    user.streak_best = max(user.streak_best, user.streak_current)
    user.last_activity_date = today_str
    db.flush()
    
    evaluate_badges(db, user)
    return True

def evaluate_badges(db: Session, user: User):
    """
    Evaluates badge unlock conditions for the given user.
    """
    all_badges = db.query(Badge).all()
    earned_badge_ids = set(b.badge_id for b in db.query(UserBadge).filter(UserBadge.user_id == user.id).all())

    # User metrics
    completed_hw_count = db.query(HomeworkAttempt).filter(
        HomeworkAttempt.user_id == user.id, HomeworkAttempt.status == "completed"
    ).count()

    attendance_count = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == user.id, AttendanceRecord.status == "present"
    ).count()

    for badge in all_badges:
        if badge.id in earned_badge_ids:
            continue

        unlocked = False
        code = badge.code.lower()

        if code == "night_owl" and completed_hw_count >= 3:
            unlocked = True
        elif code == "math_wiz" and completed_hw_count >= 1:
            unlocked = True
        elif code == "7_day_flame" and user.streak_current >= 7:
            unlocked = True
        elif code == "sat_1500_club" and user.xp >= 3000:
            unlocked = True
        elif code == "perfect_attendance" and attendance_count >= 15:
            unlocked = True
        elif code == "graphing_dynamo" and completed_hw_count >= 2:
            unlocked = True

        if unlocked:
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)

    db.flush()
