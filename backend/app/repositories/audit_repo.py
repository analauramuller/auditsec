from datetime import date

from sqlalchemy.orm import Session, joinedload

from app.domain.enums import AuditStatus
from app.models.entities import Audit, AuditResponse


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, company_id: int, module: str, audit_date: date) -> Audit:
        audit = Audit(
            company_id=company_id,
            module=module,
            audit_date=audit_date,
            status=AuditStatus.IN_PROGRESS.value,
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def get_with_responses(self, audit_id: int) -> Audit | None:
        return (
            self.db.query(Audit)
            .options(
                joinedload(Audit.company),
                joinedload(Audit.responses).joinedload(AuditResponse.control),
            )
            .filter(Audit.id == audit_id)
            .first()
        )

    def get(self, audit_id: int) -> Audit | None:
        return self.db.get(Audit, audit_id)

    def save_response(
        self,
        audit_id: int,
        control_id: int,
        status: str,
        work_in_progress: bool,
        notes: str | None,
    ) -> AuditResponse:
        existing = (
            self.db.query(AuditResponse)
            .filter(
                AuditResponse.audit_id == audit_id,
                AuditResponse.control_id == control_id,
            )
            .first()
        )
        if existing:
            existing.status = status
            existing.work_in_progress = work_in_progress
            existing.notes = notes
            response = existing
        else:
            response = AuditResponse(
                audit_id=audit_id,
                control_id=control_id,
                status=status,
                work_in_progress=work_in_progress,
                notes=notes,
            )
            self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    def finish(self, audit: Audit) -> Audit:
        from datetime import datetime

        audit.status = AuditStatus.FINISHED.value
        audit.finished_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def list_by_company(
        self, company_id: int, module: str | None = None
    ) -> list[Audit]:
        query = self.db.query(Audit).filter(Audit.company_id == company_id)
        if module:
            query = query.filter(Audit.module == module)
        return query.order_by(Audit.audit_date.desc(), Audit.created_at.desc()).all()

    def list_all_finished(self) -> list[Audit]:
        return (
            self.db.query(Audit)
            .options(joinedload(Audit.company))
            .filter(Audit.status == AuditStatus.FINISHED.value)
            .order_by(Audit.finished_at.desc())
            .all()
        )

    def list_responses(self, audit_id: int) -> list[AuditResponse]:
        return (
            self.db.query(AuditResponse)
            .filter(AuditResponse.audit_id == audit_id)
            .all()
        )

    def list_finished_by_company(
        self, company_id: int, module: str, limit: int = 3
    ) -> list[Audit]:
        return (
            self.db.query(Audit)
            .filter(
                Audit.company_id == company_id,
                Audit.module == module,
                Audit.status == AuditStatus.FINISHED.value,
            )
            .order_by(Audit.audit_date.desc(), Audit.finished_at.desc())
            .limit(limit)
            .all()
        )

    def list_finished_ids_older_than(
        self, company_id: int, module: str, keep_ids: list[int]
    ) -> list[Audit]:
        query = self.db.query(Audit).filter(
            Audit.company_id == company_id,
            Audit.module == module,
            Audit.status == AuditStatus.FINISHED.value,
        )
        if keep_ids:
            query = query.filter(Audit.id.notin_(keep_ids))
        return query.all()

    def delete_audit(self, audit: Audit) -> None:
        self.db.delete(audit)
        self.db.commit()
