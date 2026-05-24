from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.repositories.company_repo import CompanyRepository
from app.schemas.audit import AuditCreate, AuditOut, AuditStart
from app.schemas.company import CompanyCreate, CompanyDuplicateCheck, CompanyOut
from app.services.audit_service import AuditService
from app.utils.company import normalize_cnpj, normalize_name

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return CompanyRepository(db).list_all()


@router.get("/check-duplicate", response_model=CompanyDuplicateCheck)
def check_duplicate(
    name: str = Query(..., min_length=2),
    cnpj: str | None = None,
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
):
    if not CompanyRepository(db).get(company_id):
        raise HTTPException(404, "Empresa nao encontrada")
    return AuditRepository(db).list_by_company(company_id, module)


@router.post("/{company_id}/audits", response_model=AuditOut)
def start_audit_for_company(
    company_id: int,
    data: AuditStart,
    db: Session = Depends(get_db),
):
    company = CompanyRepository(db).get(company_id)
    if not company:
        raise HTTPException(404, "Empresa nao encontrada")
    service = AuditService(db)
    return service.create_audit(company_id, data.module, data.audit_date)


@router.post("", response_model=CompanyOut, status_code=201)
def create_company(data: CompanyCreate, db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    clean_cnpj = normalize_cnpj(data.cnpj)
    if data.cnpj and data.cnpj.strip() and not clean_cnpj:
        raise HTTPException(400, "CNPJ invalido. Informe 14 digitos.")
    if clean_cnpj and repo.find_by_cnpj(clean_cnpj):
        raise HTTPException(409, "CNPJ ja cadastrado no sistema.")
    if repo.find_by_name(data.name):
        raise HTTPException(409, "Nome de empresa ja cadastrado no sistema.")
    try:
        return repo.create(data.name, data.cnpj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Empresa ja cadastrada (nome ou CNPJ duplicado).")


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = CompanyRepository(db).get(company_id)
    if not company:
        raise HTTPException(404, "Empresa nao encontrada")
    return company
