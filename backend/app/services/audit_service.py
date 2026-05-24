from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.enums import AuditStatus, IsoModule, ResponseStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.company_repo import CompanyRepository
from app.repositories.control_repo import ControlRepository
from app.services.compliance_service import ComplianceService

MAX_FINISHED_AUDITS = 3


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)
        self.company_repo = CompanyRepository(db)
        self.control_repo = ControlRepository(db)
        self.compliance = ComplianceService()

    def create_audit(self, company_id: int, module: str, audit_date: date):
        if module not in {m.value for m in IsoModule}:
            raise HTTPException(400, "Modulo invalido")
        company = self.company_repo.get(company_id)
        if not company:
            raise HTTPException(404, "Empresa nao encontrada")
        return self.audit_repo.create(company_id, module, audit_date)

    def register_response(
        self,
        audit_id: int,
        control_id: int,
        status: str,
        work_in_progress: bool,
        notes: str | None,
    ):
        audit = self.audit_repo.get(audit_id)
        if not audit:
            raise HTTPException(404, "Auditoria nao encontrada")
        if audit.status == AuditStatus.FINISHED.value:
            raise HTTPException(400, "Auditoria ja finalizada")

        valid_status = {s.value for s in ResponseStatus}
        if status not in valid_status:
            raise HTTPException(400, "Status invalido")

        if status == ResponseStatus.NAO_CONFORME.value and work_in_progress:
            status = ResponseStatus.EM_ANDAMENTO.value

        control = self.control_repo.get(control_id)
        if not control or control.module != audit.module:
            raise HTTPException(400, "Controle invalido para este modulo")

        return self.audit_repo.save_response(
            audit_id, control_id, status, work_in_progress, notes
        )

    def finish_audit(self, audit_id: int):
        audit = self.audit_repo.get_with_responses(audit_id)
        if not audit:
            raise HTTPException(404, "Auditoria nao encontrada")
        if audit.status == AuditStatus.FINISHED.value:
            raise HTTPException(400, "Auditoria ja finalizada")

        controls = self.control_repo.list_by_module(audit.module)
        answered_ids = {r.control_id for r in audit.responses}
        missing = [c for c in controls if c.id not in answered_ids]
        if missing:
            raise HTTPException(
                400,
                f"Faltam {len(missing)} controles sem resposta",
            )

        audit = self.audit_repo.finish(audit)
        self._trim_old_audits(audit.company_id, audit.module)
        return audit

    def _trim_old_audits(self, company_id: int, module: str) -> None:
        finished = self.audit_repo.list_finished_by_company(
            company_id, module, limit=MAX_FINISHED_AUDITS
        )
        keep_ids = [a.id for a in finished]
        old_audits = self.audit_repo.list_finished_ids_older_than(
            company_id, module, keep_ids
        )
        for old in old_audits:
            self.audit_repo.delete_audit(old)

    def get_dashboard(self, audit_id: int) -> dict:
        audit = self.audit_repo.get_with_responses(audit_id)
        if not audit:
            raise HTTPException(404, "Auditoria nao encontrada")

        controls = self.control_repo.list_by_module(audit.module)
        summary = self.compliance.summarize_responses(controls, audit.responses)
        by_category = self.compliance.summarize_by_category(controls, audit.responses)

        return {
            "audit_id": audit.id,
            "percent_total": summary["percent_conformidade"],
            "total_controles": summary["total"],
            "conforme": summary["conforme"],
            "nao_conforme": summary["nao_conforme"],
            "em_andamento": summary["em_andamento"],
            "nao_aplica": summary["nao_aplica"],
            "by_category": by_category,
        }

    def get_comparison(self, company_id: int, module: str) -> dict:
        audits = self.audit_repo.list_finished_by_company(company_id, module)
        items = []
        for audit in reversed(audits):
            controls = self.control_repo.list_by_module(module)
            audit_full = self.audit_repo.get_with_responses(audit.id)
            summary = self.compliance.summarize_responses(
                controls, audit_full.responses if audit_full else []
            )
            items.append(
                {
                    "audit_id": audit.id,
                    "audit_date": audit.audit_date,
                    "percent_conformidade": summary["percent_conformidade"],
                }
            )
        return {"company_id": company_id, "module": module, "audits": items}
