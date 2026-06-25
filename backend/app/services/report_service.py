from pathlib import Path

from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.domain.enums import AuditStatus, ResponseStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.control_repo import ControlRepository
from app.services.audit_service import AuditService
from app.services.compliance_service import CATEGORY_LABELS, ComplianceService

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

OVERVIEW_LABELS = ["Conforme", "Nao conforme", "Em andamento", "Nao aplica"]
OVERVIEW_COLORS = ["#22c55e", "#ef4444", "#eab308", "#94a3b8"]

STATUS_ORDER = [
    ResponseStatus.CONFORME.value,
    ResponseStatus.NAO_CONFORME.value,
    ResponseStatus.EM_ANDAMENTO.value,
    ResponseStatus.NAO_APLICA.value,
    "PENDENTE",
]
STATUS_LABELS = {
    ResponseStatus.CONFORME.value: "Conforme",
    ResponseStatus.NAO_CONFORME.value: "Nao conforme",
    ResponseStatus.EM_ANDAMENTO.value: "Em andamento",
    ResponseStatus.NAO_APLICA.value: "Nao aplica",
    "PENDENTE": "Pendente",
}
STATUS_CSS = {
    ResponseStatus.CONFORME.value: "status-cell-conforme",
    ResponseStatus.NAO_CONFORME.value: "status-cell-nc",
    ResponseStatus.EM_ANDAMENTO.value: "status-cell-andamento",
    ResponseStatus.NAO_APLICA.value: "status-cell-na",
    "PENDENTE": "status-cell-pendente",
}


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

        total = sum(counts)
        if total == 0:
            counts = [1]
            display_labels = ["Sem dados"]
            pie_colors = ["#e5e7eb"]
        else:
            display_labels = [
                f"{label}\n({count})" if count else label
                for label, count in zip(labels, counts)
            ]
            pie_colors = colors
        fig, ax = plt.subplots(figsize=(2.4, 2.4))
        wedges, _, autotexts = ax.pie(
            counts,
            labels=display_labels if total else None,
            colors=pie_colors,
            autopct=lambda pct: f"{pct:.0f}%" if total and pct > 0 else "",
            startangle=90,
            textprops={"fontsize": 7},
        )
        for t in autotexts:
            t.set_fontsize(7)
        ax.set(aspect="equal")
        ax.axis("off")
        uri = self._svg_data_uri_from_figure(fig)
        plt.close(fig)
        return uri

    def _render_bar_svg(self, labels: list[str], values: list[float], color="#2563eb") -> str:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 2.8))
        x = range(len(labels))
        bars = ax.bar(x, values, color=color)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_ylabel("% Conformidade")
        ax.grid(axis="y", linestyle=":", linewidth=0.7, alpha=0.6)
        ax.bar_label(bars, fmt="%.0f%%", fontsize=8, padding=2)
        fig.tight_layout()
        uri = self._svg_data_uri_from_figure(fig)
        plt.close(fig)
        return uri

    def _render_line_svg(
        self, labels: list[str], datasets: list[dict], y_max: float = 100
    ) -> str:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 3))
        for ds in datasets:
            ax.plot(
                labels,
                ds["values"],
                marker="o",
                label=ds["label"],
                color=ds.get("color", "#2563eb"),
            )
            for x_val, y_val in zip(labels, ds["values"]):
                ax.annotate(
                    f"{y_val:.0f}%",
                    (x_val, y_val),
                    textcoords="offset points",
                    xytext=(0, 6),
                    ha="center",
                    fontsize=8,
                )
        ax.set_ylim(0, y_max)
        ax.set_ylabel("% Conformidade")
        ax.legend(fontsize=8, loc="best")
        ax.grid(axis="y", linestyle=":", linewidth=0.7, alpha=0.6)
        fig.tight_layout()
        uri = self._svg_data_uri_from_figure(fig)
        plt.close(fig)
        return uri

    def _build_charts_from_dashboard(self, dashboard: dict) -> dict:
        overview_counts = [
            dashboard["conforme"],
            dashboard["nao_conforme"],
            dashboard["em_andamento"],
            dashboard["nao_aplica"],
        ]
        overview_pie = self._render_pie_svg(
            overview_counts, OVERVIEW_LABELS, OVERVIEW_COLORS
        )

        category_pies = []
        for cat in dashboard["by_category"]:
            counts = [
                cat["conforme"],
                cat["nao_conforme"],
                cat["em_andamento"],
                cat["nao_aplica"],
            ]
            img = self._render_pie_svg(counts, OVERVIEW_LABELS, OVERVIEW_COLORS)
            category_pies.append({"label": cat["label"], "img": img})

        bar_labels = [c["label"] for c in dashboard["by_category"]]
        bar_values = [c["percent_conformidade"] for c in dashboard["by_category"]]
        bar_chart = self._render_bar_svg(bar_labels, bar_values)

        return {
            "overview_pie": overview_pie,
            "category_pies": category_pies,
            "bar_chart": bar_chart,
        }

    def _format_audit_date(self, audit_date) -> str:
        return audit_date.strftime("%d/%m/%Y")

    def _build_control_row(
        self, control, response_map: dict, include_description: bool = True
    ) -> dict:
        response = response_map.get(control.id)
        row = {
            "control_id": control.id,
            "code": control.code,
            "title": control.title,
            "category": control.category,
            "category_label": CATEGORY_LABELS.get(control.category, control.category),
            "status": response.status if response else "PENDENTE",
        }
        if include_description:
            row["description"] = control.description
        return row

    def _status_cell(self, status: str) -> dict:
        return {
            "status": status,
            "label": STATUS_LABELS.get(status, status),
            "css_class": STATUS_CSS.get(status, "status-cell-pendente"),
        }

    def _build_status_by_audit(
        self, controls: list, comparison_audits: list[dict]
    ) -> tuple[list[dict], dict[int, dict[int, str]]]:
        audit_date_columns = [
            {
                "audit_id": item["audit_id"],
                "date_label": self._format_audit_date(item["audit_date"]),
            }
            for item in comparison_audits
        ]
        status_by_audit: dict[int, dict[int, str]] = {}
        for item in comparison_audits:
            audit = self.audit_repo.get_with_responses(item["audit_id"])
            response_map = {r.control_id: r for r in (audit.responses if audit else [])}
            status_by_audit[item["audit_id"]] = {
                control.id: (
                    response_map[control.id].status
                    if control.id in response_map
                    else "PENDENTE"
                )
                for control in controls
            }
        return audit_date_columns, status_by_audit

    def _build_row_status_by_date(
        self,
        control,
        audit_date_columns: list[dict],
        status_by_audit: dict[int, dict[int, str]],
        current_audit_id: int,
    ) -> dict:
        current_status = status_by_audit.get(current_audit_id, {}).get(
            control.id, "PENDENTE"
        )
        return {
            "control_id": control.id,
            "code": control.code,
            "title": control.title,
            "description": control.description,
            "category": control.category,
            "category_label": CATEGORY_LABELS.get(control.category, control.category),
            "status": current_status,
            "status_by_date": [
                self._status_cell(
                    status_by_audit.get(col["audit_id"], {}).get(
                        control.id, "PENDENTE"
                    )
                )
                | {"date_label": col["date_label"]}
                for col in audit_date_columns
            ],
        }

    def _group_rows_by_status(self, rows: list[dict]) -> list[dict]:
        status_map: dict[str, list] = {s: [] for s in STATUS_ORDER}
        for row in rows:
            status_map.setdefault(row["status"], []).append(row)
        return [
            {
                "status": status,
                "label": STATUS_LABELS.get(status, status),
                "css_class": STATUS_CSS.get(status, "status-cell-pendente"),
                "controls": status_map[status],
            }
            for status in STATUS_ORDER
            if status_map.get(status)
        ]

    def _attach_status_groups(self, groups: list[dict]) -> list[dict]:
        for group in groups:
            group["status_groups"] = self._group_rows_by_status(group.get("controls", []))
        return groups

    def _build_comparison_control_details(
        self, controls: list, comparison_audits: list[dict], current_audit_id: int
    ) -> tuple[list[dict], list[dict]]:
        audit_date_columns, status_by_audit = self._build_status_by_audit(
            controls, comparison_audits
        )
        rows = [
            self._build_row_status_by_date(
                control, audit_date_columns, status_by_audit, current_audit_id
            )
            for control in controls
        ]
        return audit_date_columns, self._group_rows_by_status(rows)

    def _build_comparison_categories_grouped(
        self,
        controls: list,
        comparison_audits: list[dict],
        current_audit_id: int,
        dashboard: dict,
        response_map: dict,
    ) -> tuple[list[dict], list[dict]]:
        audit_date_columns, status_by_audit = self._build_status_by_audit(
            controls, comparison_audits
        )
        categories_map: dict[str, dict] = {}

        for control in controls:
            if not response_map.get(control.id):
                continue
            row = self._build_row_status_by_date(
                control, audit_date_columns, status_by_audit, current_audit_id
            )
            cat_key = control.category
            if cat_key not in categories_map:
                cat_info = next(
                    (c for c in dashboard["by_category"] if c["category"] == cat_key),
                    None,
                )
                categories_map[cat_key] = {
                    "category": cat_key,
                    "label": cat_info["label"] if cat_info else cat_key,
                    "stats": cat_info,
                    "controls": [],
                    "stats_by_date": [],
                }
            categories_map[cat_key]["controls"].append(row)

        for item in comparison_audits:
            item_dashboard = self.audit_service.get_dashboard(item["audit_id"])
            date_label = self._format_audit_date(item["audit_date"])
            for group in categories_map.values():
                cat_stats = next(
                    (
                        c
                        for c in item_dashboard["by_category"]
                        if c["category"] == group["category"]
                    ),
                    None,
                )
                group["stats_by_date"].append({
                    "date_label": date_label,
                    "stats": cat_stats,
                })

        groups = self._attach_status_groups(list(categories_map.values()))
        return audit_date_columns, groups

    def _build_comparison_summaries(
        self, comparison_audits: list[dict]
    ) -> list[dict]:
        summaries = []
        for item in comparison_audits:
            item_dashboard = self.audit_service.get_dashboard(item["audit_id"])
            summaries.append({
                "date_label": self._format_audit_date(item["audit_date"]),
                "audit_id": item["audit_id"],
                "percent_total": item_dashboard["percent_total"],
                "conforme": item_dashboard["conforme"],
                "nao_conforme": item_dashboard["nao_conforme"],
                "em_andamento": item_dashboard["em_andamento"],
                "nao_aplica": item_dashboard["nao_aplica"],
                "by_category": item_dashboard["by_category"],
            })
        return summaries

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
        comparison_chart = None
        comparison_chart_sets = []
        if mode == "comparative":
            cid = company_id or audit.company_id
            comparison = self.audit_service.get_comparison(cid, audit.module)
            if comparison and comparison["audits"]:
                dates = [
                    self._format_audit_date(a["audit_date"])
                    for a in comparison["audits"]
                ]
                comparison_chart = self._render_line_svg(
                    dates,
                    [{
                        "label": "Conformidade geral",
                        "values": [a["percent_conformidade"] for a in comparison["audits"]],
                        "color": "#2563eb",
                    }],
                )
                for item in comparison["audits"]:
                    item_dashboard = self.audit_service.get_dashboard(item["audit_id"])
                    charts = self._build_charts_from_dashboard(item_dashboard)
                    comparison_chart_sets.append({
                        "date_label": self._format_audit_date(item["audit_date"]),
                        "percent_total": item_dashboard["percent_total"],
                        "dashboard": item_dashboard,
                        **charts,
                    })

        response_map = {r.control_id: r for r in audit.responses}
        rows = []
        categories_map: dict[str, dict] = {}

        for control in controls:
            row = self._build_control_row(control, response_map)
            if report_type == "full" or response_map.get(control.id):
                rows.append(row)
            if response_map.get(control.id):
                cat_key = control.category
                if cat_key not in categories_map:
                    cat_info = next(
                        (c for c in dashboard["by_category"] if c["category"] == cat_key),
                        None,
                    )
                    categories_map[cat_key] = {
                        "category": cat_key,
                        "label": cat_info["label"] if cat_info else cat_key,
                        "stats": cat_info,
                        "controls": [],
                    }
                categories_map[cat_key]["controls"].append(row)

        categories_grouped = self._attach_status_groups(list(categories_map.values()))
        status_grouped = self._group_rows_by_status(rows)

        comparison_status_grouped = []
        comparison_categories_grouped = []
        comparison_summaries = []
        audit_date_columns = []
        comparison_dates_display = ""
        is_comparative = mode == "comparative" and comparison and comparison.get("audits")

        if is_comparative:
            comparison_summaries = self._build_comparison_summaries(comparison["audits"])
            comparison_dates_display = ", ".join(
                s["date_label"] for s in comparison_summaries
            )
            if report_type == "full":
                audit_date_columns, comparison_status_grouped = (
                    self._build_comparison_control_details(
                        controls, comparison["audits"], audit_id
                    )
                )
            else:
                audit_date_columns, comparison_categories_grouped = (
                    self._build_comparison_categories_grouped(
                        controls,
                        comparison["audits"],
                        audit_id,
                        dashboard,
                        response_map,
                    )
                )

        current_charts = self._build_charts_from_dashboard(dashboard)

        template = self.env.get_template("report.html")
        return template.render(
            audit=audit,
            company=audit.company,
            dashboard=dashboard,
            rows=rows,
            categories_grouped=categories_grouped,
            status_grouped=status_grouped,
            comparison_status_grouped=comparison_status_grouped,
            comparison_categories_grouped=comparison_categories_grouped,
            comparison_summaries=comparison_summaries,
            comparison_dates_display=comparison_dates_display,
            audit_date_columns=audit_date_columns,
            report_type=report_type,
            mode=mode,
            comparison=comparison,
            comparison_chart=comparison_chart,
            comparison_chart_sets=comparison_chart_sets,
            overview_pie=current_charts["overview_pie"],
            category_pies=current_charts["category_pies"],
            bar_chart=current_charts["bar_chart"],
        )
