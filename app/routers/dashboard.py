from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .. import models, dependencies
from ..database import get_db
from pathlib import Path
import qrcode
from io import BytesIO
from datetime import datetime, timedelta

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: models.User = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db),
    filter_user: str = None,
    filter_date: str = None
):
    query = db.query(models.Link)

    if not user.is_admin:
        query = query.filter(models.Link.user_id == user.id)
    else:
        # Admin filters
        if filter_user:
            query = query.join(models.User).filter(models.User.username == filter_user)
        
        if filter_date:
            try:
                date_obj = datetime.strptime(filter_date, '%Y-%m-%d')
                next_day = date_obj + timedelta(days=1)
                query = query.filter(models.Link.created_at >= date_obj, models.Link.created_at < next_day)
            except ValueError:
                pass 

    # Sort by newest first
    links = query.order_by(models.Link.created_at.desc()).all()
    
    all_users = []
    if user.is_admin:
        all_users = db.query(models.User).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "links": links,
        "all_users": all_users,
        "filter_user": filter_user,
        "filter_date": filter_date
    })

@router.post("/links/create")
async def create_link(
    request: Request,
    target_url: str = Form(...),
    slug: str = Form(None), # Optional custom slug
    user: models.User = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    import secrets
    import string

    # Simple normalization
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    if not slug or slug.strip() == "":
        # Generate random slug
        alphabet = string.ascii_letters + string.digits
        slug = ''.join(secrets.choice(alphabet) for _ in range(6))
        # Check collision for random slug just in case
        while db.query(models.Link).filter(models.Link.slug == slug).first():
             slug = ''.join(secrets.choice(alphabet) for _ in range(6))
    else:
        # Check collision for custom slug
        if db.query(models.Link).filter(models.Link.slug == slug).first():
            # fetch links again to re-render
            links = db.query(models.Link).filter(models.Link.user_id == user.id).order_by(models.Link.created_at.desc()).all()
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": user,
                "links": links,
                "error": f"Slug '{slug}' is already taken.",
                "last_url": target_url # preserve input
            })

    new_link = models.Link(
        slug=slug,
        target_url=target_url,
        user_id=user.id
    )
    db.add(new_link)
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/links/{link_id}/delete") # Using GET for simplicity in a pure HTML form without JS fetch, or use POST with a form
async def delete_link_get(
    request: Request,
    link_id: int,
    user: models.User = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    link = db.query(models.Link).filter(models.Link.id == link_id, models.Link.user_id == user.id).first()
    if link:
        db.delete(link)
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/links/{slug}/qrcode")
async def get_qrcode(
    request: Request,
    slug: str,
    user: models.User = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    link = db.query(models.Link).filter(models.Link.slug == slug).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Construct full URL
    base_url = str(request.base_url).rstrip("/")
    short_url = f"{base_url}/{slug}"
    
    # Generate QR Code
    img = qrcode.make(short_url)
    
    # Save to buffer
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")
