from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.app.database import get_db
from backend.app.models import User, Lesson, Homework, HomeworkAttempt, LessonProgress, AttendanceRecord
from backend.app.schemas import DashboardSchema, UserPublicSchema, LessonPublicSchema, HomeworkPublicSchema
from backend.app.deps import get_current_user
from backend.app.routers.homework import compute_homework_status
from backend.app.routers.lessons import get_lessons
from backend.app.routers.leaderboard import get_tier_name
from backend.app.services.gamification import DEFAULT_TARGET_DATE

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardSchema)
def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_date = current_user.target_test_date or DEFAULT_TARGET_DATE

    # Today's lesson
    all_lessons = get_lessons(current_user=current_user, db=db)
    today_lesson = all_lessons[0] if all_lessons else None

    # Pending homework
    homeworks = db.query(Homework).all()
    attempts_map = {
        a.homework_id: a for a in db.query(HomeworkAttempt).filter(HomeworkAttempt.user_id == current_user.id).all()
    }

    pending_hw = []
    for hw in homeworks:
        att = attempts_map.get(hw.id)
        comp_status = compute_homework_status(hw, att)
        if comp_status != "completed":
            pending_hw.append(HomeworkPublicSchema(
                id=hw.id,
                lesson_id=hw.lesson_id,
                title=hw.title,
                subject=hw.subject,
                skill=hw.skill,
                dueDate=hw.due_date,
                status=comp_status,
                questionCount=len(hw.questions),
                estTime=hw.est_time,
                xpReward=hw.xp_reward,
                score=att.score if att else None
            ))

    # Leaderboard rank calculation
    all_users = db.query(User).order_by(User.xp.desc(), User.id.asc()).all()
    user_rank = 1
    for idx, u in enumerate(all_users, start=1):
        if u.id == current_user.id:
            user_rank = idx
            break

    user_tier = get_tier_name(user_rank, current_user.xp)

    # Attendance rate
    attendance_records = db.query(AttendanceRecord).filter(AttendanceRecord.user_id == current_user.id).all()
    attended_count = sum(1 for r in attendance_records if r.status in ("present", "late"))
    total_count = len(attendance_records)
    attendance_rate = round((attended_count / total_count * 100), 1) if total_count > 0 else 94.2

    return DashboardSchema(
        user=UserPublicSchema.model_validate(current_user),
        targetDate=target_date,
        headerCountdownText="Test Day Countdown",
        todayLesson=today_lesson,
        pendingHomework=pending_hw,
        leaderboardRank=user_rank,
        leaderboardTier=user_tier,
        attendanceRate=attendance_rate
    )
