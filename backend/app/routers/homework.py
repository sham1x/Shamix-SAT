from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, Homework, Question, HomeworkAttempt, AttemptAnswer, XPEvent, UserBadge, Badge
from backend.app.schemas import (
    HomeworkPublicSchema, HomeworkDetailSchema, QuestionPublicSchema,
    QuestionAnswerSubmitSchema, HomeworkSubmitResultSchema, AnswerResultSchema
)
from backend.app.deps import get_current_user
from backend.app.services.gamification import award_xp, update_streak, evaluate_badges, get_utc_today_str

router = APIRouter(prefix="/homework", tags=["Homework"])

def compute_homework_status(hw: Homework, attempt: Optional[HomeworkAttempt]) -> str:
    if attempt:
        if attempt.status == "completed":
            return "completed"
        elif attempt.status == "in_progress":
            return "in_progress"
    
    today = get_utc_today_str()
    if hw.due_date < today:
        return "overdue"
    return "not_started"

@router.get("", response_model=List[HomeworkPublicSchema])
def get_homework_list(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    homeworks = db.query(Homework).all()
    attempts_map = {
        a.homework_id: a for a in db.query(HomeworkAttempt).filter(HomeworkAttempt.user_id == current_user.id).all()
    }

    results = []
    for hw in homeworks:
        att = attempts_map.get(hw.id)
        comp_status = compute_homework_status(hw, att)

        if status_filter and status_filter != "all" and comp_status != status_filter:
            continue

        q_count = len(hw.questions)
        score = att.score if att and att.status == "completed" else None

        results.append(HomeworkPublicSchema(
            id=hw.id,
            lesson_id=hw.lesson_id,
            title=hw.title,
            subject=hw.subject,
            skill=hw.skill,
            dueDate=hw.due_date,
            status=comp_status,
            questionCount=q_count,
            estTime=hw.est_time,
            xpReward=hw.xp_reward,
            score=score
        ))

    return results

@router.get("/{homework_id}", response_model=HomeworkDetailSchema)
def get_homework_detail(
    homework_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework assignment not found")

    att = db.query(HomeworkAttempt).filter(
        HomeworkAttempt.user_id == current_user.id,
        HomeworkAttempt.homework_id == homework_id
    ).first()

    comp_status = compute_homework_status(hw, att)
    score = att.score if att and att.status == "completed" else None

    # CRITICAL: Strip correct_index and explanation from public question schema!
    questions_public = [
        QuestionPublicSchema(
            id=q.id,
            stem=q.stem,
            options=q.options,
            topic=q.topic,
            difficulty=q.difficulty
        ) for q in hw.questions
    ]

    return HomeworkDetailSchema(
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
        score=score,
        questions=questions_public
    )

@router.post("/{homework_id}/start", response_model=dict)
def start_homework_attempt(
    homework_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework not found")

    update_streak(db, current_user)

    att = db.query(HomeworkAttempt).filter(
        HomeworkAttempt.user_id == current_user.id,
        HomeworkAttempt.homework_id == homework_id
    ).first()

    if not att:
        att = HomeworkAttempt(
            user_id=current_user.id,
            homework_id=homework_id,
            status="in_progress",
            current_question=0,
            started_at=datetime.now(timezone.utc)
        )
        db.add(att)
        db.commit()
        db.refresh(att)

    return {"attempt_id": att.id, "status": att.status, "current_question": att.current_question}

@router.post("/{homework_id}/answer", response_model=dict)
def submit_question_answer(
    homework_id: str,
    question_id: int,
    payload: QuestionAnswerSubmitSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    att = db.query(HomeworkAttempt).filter(
        HomeworkAttempt.user_id == current_user.id,
        HomeworkAttempt.homework_id == homework_id
    ).first()

    if not att:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt not started yet")

    question = db.query(Question).filter(Question.id == question_id, Question.homework_id == homework_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    is_correct = (payload.selected_index == question.correct_index)

    ans = db.query(AttemptAnswer).filter(
        AttemptAnswer.attempt_id == att.id,
        AttemptAnswer.question_id == question_id
    ).first()

    if not ans:
        ans = AttemptAnswer(
            attempt_id=att.id,
            question_id=question_id,
            selected_index=payload.selected_index,
            is_correct=is_correct
        )
        db.add(ans)
    else:
        ans.selected_index = payload.selected_index
        ans.is_correct = is_correct

    db.commit()

    return {
        "message": "Answer saved",
        "question_id": question_id,
        "selected_index": payload.selected_index,
        "correct_index": question.correct_index,
        "is_correct": is_correct,
        "explanation": question.explanation
    }

@router.post("/{homework_id}/submit", response_model=HomeworkSubmitResultSchema)
def submit_homework_attempt(
    homework_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hw = db.query(Homework).filter(Homework.id == homework_id).first()
    if not hw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Homework not found")

    att = db.query(HomeworkAttempt).filter(
        HomeworkAttempt.user_id == current_user.id,
        HomeworkAttempt.homework_id == homework_id
    ).first()

    if not att:
        att = HomeworkAttempt(
            user_id=current_user.id,
            homework_id=homework_id,
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        db.add(att)
        db.flush()

    badges_before = set(b.badge_id for b in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all())

    # Grade attempt and build detailed result breakdown
    answers_map = {ans.question_id: ans for ans in att.answers}
    results = []
    correct_count = 0
    total_q = len(hw.questions)

    for q in hw.questions:
        user_ans = answers_map.get(q.id)
        sel_idx = user_ans.selected_index if user_ans else 0
        is_corr = (sel_idx == q.correct_index)
        if is_corr:
            correct_count += 1

        results.append(AnswerResultSchema(
            question_id=q.id,
            selected_index=sel_idx,
            correct_index=q.correct_index,
            is_correct=is_corr,
            explanation=q.explanation
        ))

    score_pct = int((correct_count / total_q) * 100) if total_q > 0 else 100
    att.score = f"{score_pct}%"
    att.status = "completed"
    att.submitted_at = datetime.now(timezone.utc)
    db.flush()

    # Idempotent XP grant once per homework
    xp_granted = 0
    reason_key = f"homework_{hw.id}"
    existing_xp = db.query(XPEvent).filter(
        XPEvent.user_id == current_user.id,
        XPEvent.reason == reason_key
    ).first()

    if not existing_xp:
        award_xp(db, current_user, hw.xp_reward, reason_key)
        xp_granted = hw.xp_reward
    else:
        evaluate_badges(db, current_user)

    badges_after = set(b.badge_id for b in db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all())
    new_badge_ids = list(badges_after - badges_before)
    newly_unlocked_names = [
        b.name for b in db.query(Badge).filter(Badge.id.in_(new_badge_ids)).all()
    ] if new_badge_ids else []

    db.commit()

    return HomeworkSubmitResultSchema(
        homework_id=hw.id,
        status="completed",
        score=att.score,
        xp_rewarded=xp_granted,
        newly_unlocked_badges=newly_unlocked_names,
        results=results
    )
