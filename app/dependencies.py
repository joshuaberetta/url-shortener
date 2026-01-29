from typing import Annotated, Optional
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .auth import decode_access_token

# Let's do the query directly here to save a file, or create a crud util. 
# I'll create crud shortcuts in this file or a separate crud.py? 
# Let's just put the db query here for simplicity, or better, separate crud.py.

def get_user_from_cookie(request: Request, db: Session) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # The token coming from OAuth2PasswordBearer usually has "Bearer " prefix, but here we set cookie directly.
    # Usually we strip "Bearer " if we put it there. I will just store the raw token.
    
    payload = decode_access_token(token)
    if not payload:
        return None
        
    username: str = payload.get("sub")
    if not username:
        return None
        
    user = db.query(User).filter(User.username == username).first()
    return user

async def get_optional_user(
    request: Request, 
    db: Session = Depends(get_db)
) -> Optional[User]:
    return get_user_from_cookie(request, db)

async def get_current_user(
    request: Request,
    user: Annotated[Optional[User], Depends(get_optional_user)]
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"}
        )
    return user
