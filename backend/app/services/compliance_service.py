from app.domain.enums import ControlCategory, ResponseStatus
from app.models.entities import AuditResponse, Control

CATEGORY_LABELS = {
    ControlCategory.ORGANIZATIONAL.value: "Controles organizacionais",
    ControlCategory.PEOPLE.value: "Controles de pessoas",
    ControlCategory.PHYSICAL.value: "Controles fisicos",
    ControlCategory.TECHNOLOGICAL.value: "Controles tecnologicos",
    ControlCategory.PRIVACY.value: "Privacidade",
    "annex_a1": "Anexo A1 — Controlador de PII",
    "annex_a2": "Anexo A2 — Operador de PII",
}


class ComplianceService:
    @staticmethod
    def calculate_percent(conforme: int, nao_aplica: int, total: int) -> float:
        denominador = total - nao_aplica
        if denominador <= 0:
            return 0.0
        return round((conforme / denominador) * 100, 2)

    def summarize_responses(
        self, controls: list[Control], responses: list[AuditResponse]
    ) -> dict:
        response_map = {r.control_id: r for r in responses}
        total = len(controls)
        conforme = 0
        nao_conforme = 0
        em_andamento = 0
        nao_aplica = 0

        for control in controls:
            response = response_map.get(control.id)
            if not response:
                continue
            status = response.status
            if status == ResponseStatus.CONFORME.value:
                conforme += 1
            elif status == ResponseStatus.NAO_APLICA.value:
                nao_aplica += 1
            elif status == ResponseStatus.EM_ANDAMENTO.value:
                em_andamento += 1
            else:
                nao_conforme += 1

        percent = self.calculate_percent(conforme, nao_aplica, total)
        return {
            "total": total,
            "conforme": conforme,
            "nao_conforme": nao_conforme,
            "em_andamento": em_andamento,
            "nao_aplica": nao_aplica,
            "percent_conformidade": percent,
        }

    def summarize_by_category(
        self, controls: list[Control], responses: list[AuditResponse]
    ) -> list[dict]:
        response_map = {r.control_id: r for r in responses}
        categories: dict[str, list[Control]] = {}
        for control in controls:
            categories.setdefault(control.category, []).append(control)

        results = []
        for category, cat_controls in sorted(categories.items()):
            conforme = 0
            nao_conforme = 0
            em_andamento = 0
            nao_aplica = 0
            for control in cat_controls:
                response = response_map.get(control.id)
                if not response:
                    continue
                status = response.status
                if status == ResponseStatus.CONFORME.value:
                    conforme += 1
                elif status == ResponseStatus.NAO_APLICA.value:
                    nao_aplica += 1
                elif status == ResponseStatus.EM_ANDAMENTO.value:
                    em_andamento += 1
                else:
                    nao_conforme += 1
            total = len(cat_controls)
            results.append(
                {
                    "category": category,
                    "label": CATEGORY_LABELS.get(category, category),
                    "total": total,
                    "conforme": conforme,
                    "nao_conforme": nao_conforme,
                    "em_andamento": em_andamento,
                    "nao_aplica": nao_aplica,
                    "percent_conformidade": self.calculate_percent(
                        conforme, nao_aplica, total
                    ),
                }
            )
        return results
