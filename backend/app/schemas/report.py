from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ReportCatalogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: int
    company_id: int
    company_name: str
    module: str
    audit_date: date
    finished_at: datetime | None
