from datetime import date, datetime

from pydantic import BaseModel, Field


class AuditCreate(BaseModel):
    company_id: int
    module: str
    audit_date: date


class AuditStart(BaseModel):
    module: str
    audit_date: date


class AuditOut(BaseModel):
    id: int
    company_id: int
    module: str
    audit_date: date
    status: str
    finished_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditResponseIn(BaseModel):
    control_id: int
    status: str
    work_in_progress: bool = False
    notes: str | None = None


class AuditResponseOut(BaseModel):
    id: int
    control_id: int
    status: str
    work_in_progress: bool
    notes: str | None

    class Config:
        from_attributes = True


class CategoryStats(BaseModel):
    category: str
    label: str
    total: int
    conforme: int
    nao_conforme: int
    em_andamento: int
    nao_aplica: int
    percent_conformidade: float


class DashboardOut(BaseModel):
    audit_id: int
    percent_total: float
    total_controles: int
    conforme: int
    nao_conforme: int
    em_andamento: int
    nao_aplica: int
    by_category: list[CategoryStats]


class AuditComparisonItem(BaseModel):
    audit_id: int
    audit_date: date
    percent_conformidade: float


class ComparisonOut(BaseModel):
    company_id: int
    module: str
    audits: list[AuditComparisonItem]
