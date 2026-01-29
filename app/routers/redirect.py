from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db

router = APIRouter()

@router.get("/{slug}")
async def redirect_to_url(
    slug: str,
    db: Session = Depends(get_db)
):
    link = db.query(models.Link).filter(models.Link.slug == slug).first()
    if not link:
        # Fallback or 404
        raise HTTPException(status_code=404, detail="Link not found")

    # Increment clicks
    # Atomic update usually preferred, but for this simple app:
    link.click_count += 1
    db.commit()

    return RedirectResponse(url=link.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
