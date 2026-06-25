from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_auth, require_company_access
from app.database import get_db
from app.models.entities import User
from app.repositories.audit_repo import AuditRepository
from app.repositories.company_repo import CompanyRepository
from app.schemas.audit import AuditCreate, AuditOut, AuditStart
from app.schemas.company import CompanyCreate, CompanyDuplicateCheck, CompanyOut
from app.services.audit_service import AuditService
from app.utils.company import normalize_cnpj, normalize_name

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    return CompanyRepository(db).list_by_user(current_user.id)


@router.get("/check-duplicate", response_model=CompanyDuplicateCheck)
def check_duplicate(
    name: str = Query(..., min_length=2),
    cnpj: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    repo = CompanyRepository(db)
    clean_cnpj = normalize_cnpj(cnpj)
    if cnpj and cnpj.strip() and not clean_cnpj:
        return CompanyDuplicateCheck(
            available=False,
            conflict_field="cnpj",
            message="CNPJ invalido. Informe 14 digitos.",
        )
    if clean_cnpj and repo.find_by_cnpj(clean_cnpj):
        return CompanyDuplicateCheck(
            available=False,
            conflict_field="cnpj",
            message="CNPJ ja cadastrado no sistema.",
        )
    if repo.find_by_name(name):
        return CompanyDuplicateCheck(
            available=False,
            conflict_field="name",
            message="Nome de empresa ja cadastrado no sistema.",
        )
    return CompanyDuplicateCheck(available=True)


@router.get("/{company_id}/audits", response_model=list[AuditOut])
def list_company_audits(
    company_id: int,
    module: str | None = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    require_company_access(company_id, current_user, db)
    return AuditRepository(db).list_by_company(company_id, module)


@router.post("/{company_id}/audits", response_model=AuditOut)
def start_audit_for_company(
    company_id: int,
    data: AuditStart,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    require_company_access(company_id, current_user, db)
    service = AuditService(db)
    return service.create_audit(company_id, data.module, data.audit_date)


@router.post("", response_model=CompanyOut, status_code=201)
def create_company(
    data: CompanyCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    repo = CompanyRepository(db)
    clean_cnpj = normalize_cnpj(data.cnpj)
    if data.cnpj and data.cnpj.strip() and not clean_cnpj:
        raise HTTPException(400, "CNPJ invalido. Informe 14 digitos.")
    if clean_cnpj and repo.find_by_cnpj(clean_cnpj):
        raise HTTPException(409, "CNPJ ja cadastrado no sistema.")
    if repo.find_by_name(data.name):
        raise HTTPException(409, "Nome de empresa ja cadastrado no sistema.")
    try:
        return repo.create(data.name, data.cnpj, current_user.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Empresa ja cadastrada (nome ou CNPJ duplicado).")


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    return require_company_access(company_id, current_user, db)
