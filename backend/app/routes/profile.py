from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_or_create_profile, get_profile
from app.generate import apply_targets, regenerate_plan
from app.nutrition import compute_targets
from app.schemas import ProfileIn
from app.serializers import profile_out, targets_out

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile")
def read_profile(db: Session = Depends(get_db)):
    profile = get_profile(db)
    return {"profile": profile_out(profile) if profile else None, "onboarded": profile is not None}


@router.post("/profile/preview")
def preview_targets(payload: ProfileIn):
    """Same maths as saving, so the wizard can show the real numbers up front."""
    targets = compute_targets(
        sex=payload.sex,
        age=payload.age,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        goal=payload.goal,
        activity_level=payload.activity_level,
    )
    return asdict(targets)


@router.put("/profile")
def save_profile(payload: ProfileIn, db: Session = Depends(get_db)):
    profile = get_or_create_profile(db)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    apply_targets(profile)
    db.commit()

    regenerate_plan(db, profile)
    db.refresh(profile)
    return {"profile": profile_out(profile)}


@router.get("/targets")
def read_targets(db: Session = Depends(get_db)):
    profile = get_profile(db)
    if profile is None:
        raise HTTPException(status_code=404, detail="No profile yet")
    return targets_out(profile)
