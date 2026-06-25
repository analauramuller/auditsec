from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Audit, Company, User
from app.repositories.audit_repo import AuditRepository
from app.repositories.company_repo import CompanyRepository


def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Nao autenticado")
    user = db.get(User, user_id)
    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Sessao invalida")
    return user


def require_company_access(
    company_id: int, user: User, db: Session
) -> Company:
    company = CompanyRepository(db).get_for_user(company_id, user.id)
    if not company:
        raise HTTPException(404, "Empresa nao encontrada")
    return company


def require_audit_access(audit_id: int, user: User, db: Session) -> Audit:
    audit = AuditRepository(db).get(audit_id)
    if not audit:
        raise HTTPException(404, "Auditoria nao encontrada")
    require_company_access(audit.company_id, user, db)
    return audit

