from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_auth
from app.database import get_db
from app.models.entities import User
from app.schemas.auth import LoginIn, UserOut
from app.utils.password import validate_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserOut)
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    validate_password(data.password)
    user = (
        db.query(User)
        .filter(func.lower(User.login) == data.login.strip().lower())
        .first()
    )
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Login ou senha invalidos")
    request.session.clear()
    request.session["user_id"] = user.id
    return user


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(require_auth)):
    return current_user


@router.post("/register", response_model=UserOut)
def register(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    """Cria um novo usuario sem criptografia (intencional) e inicia sessao.

    Regras simples:
    - login obrigatorio (trim)
    - senha validada por validate_password
    - login unico (case-insensitive)
    """
    # valida senha
    validate_password(data.password)

    login_clean = (data.login or "").strip()
    if not login_clean:
        raise HTTPException(status_code=400, detail="Login obrigatorio")

    # verifica duplicado (case-insensitive)
    existing = db.query(User).filter(func.lower(User.login) == login_clean.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Login ja existe")

    # cria usuario (sem hash, conforme solicitado)
    user = User(login=login_clean, password=data.password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # inicia sessao
    request.session.clear()
    request.session["user_id"] = user.id

    return user

