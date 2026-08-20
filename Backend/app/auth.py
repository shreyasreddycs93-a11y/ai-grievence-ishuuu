"""
Password hashing and JWT helpers shared by app/routers/auth.py and, later,
by any route that needs to require a logged-in officer/citizen.
"""
from datetime import datetime, timedelta, timezone

from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Account

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(account: Account) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(account.id), "role": account.role.value, "exp": expires_at}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Account:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    account = db.get(Account, int(payload["sub"]))
    if account is None:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return account


def get_current_account_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[Account]:
    """Same as get_current_account, but for routes usable both logged-in and
    anonymously (e.g. /intake/web) — no/invalid token just means None,
    never a 401."""
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return db.get(Account, int(payload["sub"]))


def require_officer(account: Account = Depends(get_current_account)) -> Account:
    if account.role.value != "officer":
        raise HTTPException(status_code=403, detail="Officer access required")
    return account
