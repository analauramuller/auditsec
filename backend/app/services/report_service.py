from pathlib import Path

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.domain.enums import AuditStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.control_repo import ControlRepository
from app.services.audit_service import AuditService
from app.services.compliance_service import ComplianceService

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditRepository(db)
        self.control_repo = ControlRepository(db)
        self.compliance = ComplianceService()
        self.audit_service = AuditService(db)
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html"]),
        )

    def generate_html(
        self,
        audit_id: int,
        report_type: str,
        mode: str,
        company_id: int | None = None,
    ) -> str:
        audit = self.audit_repo.get_with_responses(audit_id)
        if not audit:
            raise HTTPException(404, "Auditoria nao encontrada")
        if audit.status != AuditStatus.FINISHED.value:
            raise HTTPException(400, "Relatorio disponivel apenas apos finalizacao")

        controls = self.control_repo.list_by_module(audit.module)
        dashboard = self.audit_service.get_dashboard(audit_id)
        comparison = None
        if mode == "comparative" and company_id:
            comparison = self.audit_service.get_comparison(company_id, audit.module)

        response_map = {r.control_id: r for r in audit.responses}
        rows = []
        for control in controls:
            response = response_map.get(control.id)
            if report_type == "by_category" and not response:
                continue
            rows.append(
                {
                    "code": control.code,
                    "title": control.title,
                    "description": control.description,
                    "category": control.category,
                    "status": response.status if response else "PENDENTE",
                }
            )

        template = self.env.get_template("report.html")
        return template.render(
            audit=audit,
            company=audit.company,
            dashboard=dashboard,
            rows=rows,
            report_type=report_type,
            mode=mode,
            comparison=comparison,
        )
