from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Profile

PROFILE_ID = 1


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_profile(db: Session) -> Profile | None:
    return db.get(Profile, PROFILE_ID)


def get_or_create_profile(db: Session) -> Profile:
    profile = get_profile(db)
    if profile is None:
        profile = Profile(id=PROFILE_ID)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
