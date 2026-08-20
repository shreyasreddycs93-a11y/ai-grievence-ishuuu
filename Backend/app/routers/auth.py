"""
Account signup/login for the Landing app. Distinct from the WhatsApp-sourced
`User` profile in app/models.py — this is credentialed login for the citizen
and officer web apps.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_account, hash_password, verify_password
from app.config import settings
from app.db import get_db
from app.models import Account, AccountRole, Department
from app.schemas import AccountOut, AuthResponse, LoginRequest, SignupRequest

router = APIRouter(tags=["auth"])


def _to_account_out(account: Account) -> AccountOut:
    return AccountOut(
        id=account.id,
        name=account.name,
        email=account.email,
        role=account.role,
        department_id=account.department_id,
    )


@router.post("/auth/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(Account).filter(Account.email == payload.email).first() is not None:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    if payload.role == AccountRole.officer:
        if payload.invite_code != settings.DEPARTMENT_INVITE_CODE:
            raise HTTPException(status_code=403, detail="Invalid officer invite code")
        if payload.department_id is None:
            raise HTTPException(status_code=422, detail="department_id is required for officer accounts")
        if db.get(Department, payload.department_id) is None:
            raise HTTPException(status_code=404, detail="Department not found")

    account = Account(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        department_id=payload.department_id if payload.role == AccountRole.officer else None,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    return AuthResponse(access_token=create_access_token(account), account=_to_account_out(account))


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.email == payload.email).first()
    if account is None or not verify_password(payload.password, account.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return AuthResponse(access_token=create_access_token(account), account=_to_account_out(account))


@router.get("/auth/me", response_model=AccountOut)
def me(account: Account = Depends(get_current_account)):
    return _to_account_out(account)
