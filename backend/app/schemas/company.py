from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2)
    cnpj: str | None = None


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cnpj: str | None
    created_at: datetime


class CompanyDuplicateCheck(BaseModel):
    available: bool
    conflict_field: str | None = None
    message: str | None = None
