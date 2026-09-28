from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import UserRegisterSchema, UserLoginSchema, TokenSchema, UserPublicSchema, UserUpdateSchema
from backend.app.security import hash_password, verify_password, create_access_token
from backend.app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

# In-memory rate limiting dictionary for login/register endpoints
_rate_limit_store = {}

def check_rate_limit(client_ip: str, limit: int = 20, window_sec: int = 60):
    now = datetime.now(timezone.utc).timestamp()
    history = _rate_limit_store.get(client_ip, [])
    history = [t for t in history if now - t < window_sec]
    if len(history) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please wait a minute."
        )
    history.append(now)
    _rate_limit_store[client_ip] = history

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(request: Request, payload: UserRegisterSchema, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if not payload.password[0].isupper():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must start with a capital letter (A-Z)"
        )
    if not any(c.isdigit() for c in payload.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )
    if not any(not c.isalnum() for c in payload.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one special symbol (!@#$%^&*)"
        )

    # Check existing username
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check existing email
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pw = hash_password(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hashed_pw,
        display_name=payload.display_name or payload.username,
        xp=0,
        level=1,
        streak_current=0,
        streak_best=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserPublicSchema.model_validate(user)
    }

@router.post("/login", response_model=dict)
def login_user(request: Request, payload: UserLoginSchema, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(client_ip)

    user = db.query(User).filter(User.username == payload.username).first()
    
    # Generic error message to prevent username enumeration
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserPublicSchema.model_validate(user)
    }

@router.get("/me", response_model=UserPublicSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserPublicSchema)
def update_me(
    payload: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.target_test_date is not None:
        current_user.target_test_date = payload.target_test_date

    db.commit()
    db.refresh(current_user)
    return current_user
