from fastapi import APIRouter

from app.config import APP_VERSION, SITE_TITLE

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/site")
def site():
    return {"title": SITE_TITLE, "version": APP_VERSION}
