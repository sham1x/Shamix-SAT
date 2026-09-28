from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models import User, XPEvent
from backend.app.schemas import LeaderboardSchema, LeaderboardEntrySchema
from backend.app.deps import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

def get_tier_name(rank: int, xp: int) -> str:
    if rank == 1 or xp >= 5000:
        return "Cosmic Legend 👑"
    elif rank <= 3 or xp >= 3400:
        return "Diamond I 💎"
    elif rank <= 5 or xp >= 2800:
        return "Platinum IV 🛡️"
    elif rank <= 10 or xp >= 2000:
        return "Gold I 🥇"
    return "Silver Tier 🛡️"

@router.get("", response_model=LeaderboardSchema)
def get_leaderboard(
    period: str = Query("all_time", pattern="^(week|all_time)$"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    if period == "week":
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        # Aggregate weekly XP from XPEvent
        weekly_xp_rows = db.query(
            XPEvent.user_id, func.sum(XPEvent.amount).label("week_xp")
        ).filter(XPEvent.created_at >= seven_days_ago).group_by(XPEvent.user_id).all()
        
        weekly_map = {row.user_id: row.week_xp for row in weekly_xp_rows}
        user_scores = [(u, weekly_map.get(u.id, 0)) for u in users]
    else:
        user_scores = [(u, u.xp) for u in users]

    # Sort by score DESC, then user.id ASC (tie breaker)
    user_scores.sort(key=lambda x: (-x[1], x[0].id))

    standings = []
    current_user_entry = None

    for rank_idx, (u, score) in enumerate(user_scores, start=1):
        is_user = (u.id == current_user.id)
        tier = get_tier_name(rank_idx, score)

        entry = LeaderboardEntrySchema(
            rank=rank_idx,
            name=f"{u.display_name} (You)" if is_user else u.display_name,
            xp=score,
            streak=u.streak_current,
            badge=tier,
            isUser=is_user
        )

        if rank_idx <= limit:
            standings.append(entry)

        if is_user:
            current_user_entry = entry

    if not current_user_entry:
        current_user_entry = LeaderboardEntrySchema(
            rank=len(user_scores) + 1,
            name=f"{current_user.display_name} (You)",
            xp=current_user.xp,
            streak=current_user.streak_current,
            badge=get_tier_name(len(user_scores) + 1, current_user.xp),
            isUser=True
        )

    return LeaderboardSchema(
        standings=standings,
        userRank=current_user_entry
    )
