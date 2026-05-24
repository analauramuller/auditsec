from pydantic import BaseModel


class ModuleOut(BaseModel):
    id: str
    name: str
    description: str
    catalog_ref: str


class ControlOut(BaseModel):
    id: int
    module: str
    code: str
    title: str
    category: str
    catalog_version: str
    description: str | None = None

    model_config = {"from_attributes": True}
