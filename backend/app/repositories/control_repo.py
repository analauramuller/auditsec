from sqlalchemy.orm import Session

from app.models.entities import Control


class ControlRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_module(self, module: str) -> list[Control]:
        return (
            self.db.query(Control)
            .filter(Control.module == module)
            .order_by(Control.code)
            .all()
        )

    def get(self, control_id: int) -> Control | None:
        return self.db.get(Control, control_id)

    def count_by_module(self, module: str) -> int:
        return self.db.query(Control).filter(Control.module == module).count()
