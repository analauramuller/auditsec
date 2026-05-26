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

    # Geracao de imagens (SVG) via matplotlib para inclusão no HTML (data URI)
    def _svg_data_uri_from_figure(self, fig) -> str:
        import io, base64

        buf = io.BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        buf.seek(0)
        svg_bytes = buf.read()
        encoded = base64.b64encode(svg_bytes).decode("ascii")
        return f"data:image/svg+xml;base64,{encoded}"

    def _render_pie_svg(
        self, counts: list[int], labels: list[str], colors: list[str] | None = None
    ) -> str:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(2.0, 2.0))
        ax.pie(counts, labels=None, colors=colors, autopct=None, startangle=90)
        ax.set(aspect="equal")
        ax.axis("off")
        uri = self._svg_data_uri_from_figure(fig)
        plt.close(fig)
        return uri

    def _render_bar_svg(self, labels: list[str], values: list[float], color="#2563eb") -> str:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 2.6))
        x = range(len(labels))
        ax.bar(x, values, color=color)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_ylabel("% Conformidade")
        ax.grid(axis="y", linestyle=":", linewidth=0.7, alpha=0.6)
        fig.tight_layout()
        uri = self._svg_data_uri_from_figure(fig)
        plt.close(fig)
        return uri

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
        # Gerar imagens SVG para inclusão no relatorio (data URIs)
        # Overview pie (visao geral)
        overview_counts = [
            dashboard["conforme"],
            dashboard["nao_conforme"],
            dashboard["em_andamento"],
            dashboard["nao_aplica"],
        ]
        overview_labels = ["Conforme", "Nao conforme", "Em andamento", "Nao aplica"]
        overview_colors = ["#22c55e", "#ef4444", "#eab308", "#94a3b8"]
        overview_pie = self._render_pie_svg(
            overview_counts, overview_labels, overview_colors
        )

        # Per-category pies
        category_pies = []
        for cat in dashboard["by_category"]:
            counts = [
                cat["conforme"],
                cat["nao_conforme"],
                cat["em_andamento"],
                cat["nao_aplica"],
            ]
            img = self._render_pie_svg(counts, overview_labels, overview_colors)
            category_pies.append({"label": cat["label"], "img": img})

        # Bar chart (percent by category)
        bar_labels = [c["label"] for c in dashboard["by_category"]]
        bar_values = [c["percent_conformidade"] for c in dashboard["by_category"]]
        bar_chart = self._render_bar_svg(bar_labels, bar_values)

        return template.render(
            audit=audit,
            company=audit.company,
            dashboard=dashboard,
            rows=rows,
            report_type=report_type,
            mode=mode,
            comparison=comparison,
            overview_pie=overview_pie,
            category_pies=category_pies,
            bar_chart=bar_chart,
        )
