from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Company
from app.utils.company import normalize_cnpj, normalize_name


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, cnpj: str | None) -> Company:
        clean_name = normalize_name(name)
        clean_cnpj = normalize_cnpj(cnpj)
        company = Company(name=clean_name, cnpj=clean_cnpj)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def find_by_name(self, name: str) -> Company | None:
        clean = normalize_name(name)
        return (
            self.db.query(Company)
            .filter(func.lower(Company.name) == clean.lower())
            .first()
        )

    def find_by_cnpj(self, cnpj: str | None) -> Company | None:
        clean = normalize_cnpj(cnpj)
        if not clean:
            return None
        return self.db.query(Company).filter(Company.cnpj == clean).first()

    def list_all(self) -> list[Company]:
        return self.db.query(Company).order_by(Company.name).all()
