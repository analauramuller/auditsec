from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.control_repo import ControlRepository
from app.schemas.control import ControlOut

router = APIRouter(prefix="/controls", tags=["controls"])


@router.get("", response_model=list[ControlOut])
def list_controls(module: str = Query(...), db: Session = Depends(get_db)):
    repo = ControlRepository(db)
    return repo.list_by_module(module)
