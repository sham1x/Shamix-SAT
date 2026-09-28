from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Flashcard
from backend.app.schemas import FlashcardSchema
from backend.app.deps import get_current_user

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])

@router.get("", response_model=List[FlashcardSchema])
def get_flashcards(
    deck: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Flashcard)
    if deck:
        query = query.filter(Flashcard.deck == deck)
    cards = query.all()
    return cards
