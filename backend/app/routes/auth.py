from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.config import ALLOW_REGISTRATION, MAX_USERS
from app.deps import get_current_user, get_db, get_profile
from app.models import Profile, User
from app.schemas import LoginIn, RegisterIn
from app.serializers import user_out

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: User) -> dict:
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user_out(user)}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if not ALLOW_REGISTRATION:
        raise HTTPException(status_code=403, detail="Registration is closed on this server")

    if db.query(User).count() >= MAX_USERS:
        raise HTTPException(status_code=403, detail="This server has reached its account limit")

    username = payload.username.strip()
    existing = db.query(User).filter(User.username.ilike(username)).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="That username is already taken")

    user = User(username=username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username.ilike(payload.username.strip())).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        # Same message either way, so the response can't be used to find usernames.
        raise HTTPException(status_code=401, detail="Wrong username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="That account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_profile(db, user)
    return {"user": user_out(user), "onboarded": profile is not None}
