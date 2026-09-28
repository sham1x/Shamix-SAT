from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, AttendanceRecord, ClassSession, XPEvent
from backend.app.schemas import AttendanceSchema, AttendanceSessionSchema, CheckInResponseSchema
from backend.app.deps import get_current_user
from backend.app.services.gamification import award_xp, update_streak, get_utc_today_str

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.get("", response_model=AttendanceSchema)
def get_attendance(
    month: Optional[str] = Query(None, pattern="^\\d{4}-\\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_month = month or datetime.now(timezone.utc).strftime("%Y-%m")
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.check_date.like(f"{target_month}%")
    ).all()

    days_attended = []
    days_missed = []

    for r in records:
        try:
            day_num = int(r.check_date.split("-")[2])
            if r.status in ("present", "late"):
                days_attended.append(day_num)
            else:
                days_missed.append(day_num)
        except Exception:
            pass

    total_days = len(days_attended) + len(days_missed)
    rate = round((len(days_attended) / total_days * 100), 1) if total_days > 0 else 94.2

    sessions = db.query(ClassSession).order_by(ClassSession.date).all()
    upcoming = [
        AttendanceSessionSchema(
            day=s.day_num,
            title=s.title,
            time=s.time,
            instructor=s.instructor
        ) for s in sessions
    ]

    return AttendanceSchema(
        daysAttended=days_attended,
        daysMissed=days_missed,
        attendanceRate=rate,
        upcomingLiveSessions=upcoming
    )

@router.post("/check-in", response_model=CheckInResponseSchema)
def daily_check_in(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today_str = get_utc_today_str()
    reason_key = f"daily_checkin_{today_str}"

    existing_checkin = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id,
        AttendanceRecord.check_date == today_str
    ).first()

    if existing_checkin:
        return CheckInResponseSchema(
            message="✨ You have already checked in today! Streak active.",
            xp_reward=0,
            current_streak=current_user.streak_current
        )

    # Log attendance
    rec = AttendanceRecord(
        user_id=current_user.id,
        check_date=today_str,
        status="present",
        checked_in_at=datetime.now(timezone.utc)
    )
    db.add(rec)

    # Update streak
    update_streak(db, current_user)

    # Idempotent XP grant
    award_xp(db, current_user, 50, reason_key)
    db.commit()

    return CheckInResponseSchema(
        message=f"🎉 Daily Check-In Complete! You earned +50 Stardust XP!",
        xp_reward=50,
        current_streak=current_user.streak_current
    )
