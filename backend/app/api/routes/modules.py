from fastapi import APIRouter

from app.schemas.control import ModuleOut

router = APIRouter(prefix="/modules", tags=["modules"])

MODULES = [
    ModuleOut(
        id="ISO27001",
        name="NBR ISO/IEC 27001",
        description="SGSI — diagnostico de conformidade com base na NBR ISO/IEC 27002:2022 (93 controles)",
        catalog_ref="NBR ISO/IEC 27002:2022",
    ),
    ModuleOut(
        id="ISO27701",
        name="NBR ISO/IEC 27701",
        description="PIMS — privacidade e PII com base nos Anexos A1 e A2 (49 controles)",
        catalog_ref="NBR ISO/IEC 27701:2026",
    ),
]


@router.get("", response_model=list[ModuleOut])
def list_modules():
    return MODULES
