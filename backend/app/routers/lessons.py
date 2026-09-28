from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, Lesson, LessonProgress
from backend.app.schemas import LessonPublicSchema, LessonProgressUpdateSchema
from backend.app.deps import get_current_user

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.get("", response_model=List[LessonPublicSchema])
def get_lessons(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lessons = db.query(Lesson).order_by(Lesson.order).all()
    user_progress_map = {
        p.lesson_id: p for p in db.query(LessonProgress).filter(LessonProgress.user_id == current_user.id).all()
    }

    results = []
    for les in lessons:
        p = user_progress_map.get(les.id)
        watched = p.watched_seconds if p else 0
        completed = p.completed if p else False
        progress_pct = 100 if completed else (int((watched / les.duration_sec) * 100) if les.duration_sec > 0 else 0)

        materials = les.materials or {}
        results.append(LessonPublicSchema(
            id=les.id,
            title=les.title,
            subject=les.subject,
            module=les.module,
            duration=les.duration_str,
            duration_sec=les.duration_sec,
            progress=min(100, progress_pct),
            completed=completed,
            videoUrl=les.video_url,
            description=les.description,
            keyTakeaways=materials.get("keyTakeaways", []),
            transcript=materials.get("transcript", []),
            relatedHomeworkId=materials.get("relatedHomeworkId")
        ))
    return results

@router.get("/{lesson_id}", response_model=LessonPublicSchema)
def get_lesson_detail(lesson_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    les = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not les:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    p = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()

    watched = p.watched_seconds if p else 0
    completed = p.completed if p else False
    progress_pct = 100 if completed else (int((watched / les.duration_sec) * 100) if les.duration_sec > 0 else 0)
    materials = les.materials or {}

    return LessonPublicSchema(
        id=les.id,
        title=les.title,
        subject=les.subject,
        module=les.module,
        duration=les.duration_str,
        duration_sec=les.duration_sec,
        progress=min(100, progress_pct),
        completed=completed,
        videoUrl=les.video_url,
        description=les.description,
        keyTakeaways=materials.get("keyTakeaways", []),
        transcript=materials.get("transcript", []),
        relatedHomeworkId=materials.get("relatedHomeworkId")
    )

@router.post("/{lesson_id}/progress", response_model=dict)
def update_lesson_progress(
    lesson_id: str,
    payload: LessonProgressUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    les = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not les:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    p = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id
    ).first()

    if not p:
        p = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            watched_seconds=payload.watched_seconds,
            completed=payload.completed or False
        )
        db.add(p)
    else:
        p.watched_seconds = max(p.watched_seconds, payload.watched_seconds)
        if payload.completed:
            p.completed = True

    db.commit()
    return {"message": "Lesson progress updated", "completed": p.completed}
