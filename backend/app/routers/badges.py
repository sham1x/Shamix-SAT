from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, Badge, UserBadge, HomeworkAttempt, AttendanceRecord
from backend.app.schemas import BadgePublicSchema
from backend.app.deps import get_current_user

router = APIRouter(prefix="/badges", tags=["Badges"])

@router.get("", response_model=List[BadgePublicSchema])
def get_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    all_badges = db.query(Badge).all()
    user_badges_map = {
        ub.badge_id: ub for ub in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    }

    completed_hw_count = db.query(HomeworkAttempt).filter(
        HomeworkAttempt.user_id == current_user.id, HomeworkAttempt.status == "completed"
    ).count()

    attendance_count = db.query(AttendanceRecord).filter(
        AttendanceRecord.user_id == current_user.id, AttendanceRecord.status == "present"
    ).count()

    results = []
    for b in all_badges:
        earned = b.id in user_badges_map
        prog_str = "0/1"

        code = b.code.lower()
        if code == "night_owl":
            prog_str = f"{min(3, completed_hw_count)}/3"
        elif code == "math_wiz":
            prog_str = f"{min(5, completed_hw_count)}/5"
        elif code == "7_day_flame":
            prog_str = f"{min(7, current_user.streak_current)}/7"
        elif code == "sat_1500_club":
            prog_str = f"{current_user.xp}/1500"
        elif code == "perfect_attendance":
            prog_str = f"{min(15, attendance_count)}/15"
        elif code == "graphing_dynamo":
            prog_str = f"{min(10, completed_hw_count * 5)}/10"

        if earned:
            prog_str = b.criteria.get("target_progress", "Done") if b.criteria else "Completed"

        results.append(BadgePublicSchema(
            id=b.id,
            code=b.code,
            title=b.name,
            desc=b.description,
            unlocked=earned,
            progress=prog_str,
            icon=b.icon
        ))

    return results
