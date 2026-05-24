from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.audit_repo import AuditRepository
from app.schemas.audit import (
    AuditCreate,
    AuditOut,
    AuditResponseIn,
    AuditResponseOut,
    ComparisonOut,
    DashboardOut,
)
from app.schemas.report import ReportCatalogItem
from app.services.audit_service import AuditService
from app.services.report_service import ReportService

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("/reports/catalog", response_model=list[ReportCatalogItem])
def list_reports_catalog(db: Session = Depends(get_db)):
    repo = AuditRepository(db)
    audits = repo.list_all_finished()
    return [
        ReportCatalogItem(
            audit_id=a.id,
            company_id=a.company_id,
            company_name=a.company.name,
            module=a.module,
            audit_date=a.audit_date,
            finished_at=a.finished_at,
        )
        for a in audits
    ]


@router.get("/{audit_id}/responses", response_model=list[AuditResponseOut])
def list_audit_responses(audit_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    repo = AuditRepository(db)
    if not repo.get(audit_id):
        raise HTTPException(404, "Auditoria nao encontrada")
    return repo.list_responses(audit_id)


@router.post("", response_model=AuditOut)
def create_audit(data: AuditCreate, db: Session = Depends(get_db)):
    service = AuditService(db)
    return service.create_audit(data.company_id, data.module, data.audit_date)


@router.get("/{audit_id}", response_model=AuditOut)
def get_audit(audit_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    repo = AuditRepository(db)
    audit = repo.get(audit_id)
    if not audit:
        raise HTTPException(404, "Auditoria nao encontrada")
    return audit


@router.patch("/{audit_id}/responses", response_model=AuditResponseOut)
def register_response(
    audit_id: int, data: AuditResponseIn, db: Session = Depends(get_db)
):
    service = AuditService(db)
    return service.register_response(
        audit_id, data.control_id, data.status, data.work_in_progress, data.notes
    )


@router.post("/{audit_id}/finish", response_model=AuditOut)
def finish_audit(audit_id: int, db: Session = Depends(get_db)):
    service = AuditService(db)
    return service.finish_audit(audit_id)


@router.get("/{audit_id}/dashboard", response_model=DashboardOut)
def get_dashboard(audit_id: int, db: Session = Depends(get_db)):
    service = AuditService(db)
    return service.get_dashboard(audit_id)


@router.get("/{audit_id}/reports", response_class=HTMLResponse)
def get_report(
    audit_id: int,
    type: str = Query("full", alias="type"),
    mode: str = Query("current"),
    company_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = ReportService(db)
    return service.generate_html(audit_id, type, mode, company_id)


@router.get("/company/{company_id}/history", response_model=list[AuditOut])
def list_company_finished_history(
    company_id: int,
    module: str = Query(...),
    limit: int = Query(3, le=3),
    db: Session = Depends(get_db),
):
    repo = AuditRepository(db)
    return repo.list_finished_by_company(company_id, module, limit)


@router.get("/company/{company_id}/comparison", response_model=ComparisonOut)
def get_comparison(
    company_id: int, module: str = Query(...), db: Session = Depends(get_db)
):
    service = AuditService(db)
    return service.get_comparison(company_id, module)
