from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Company
from app.utils.company import normalize_cnpj, normalize_name


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, cnpj: str | None, user_id: int) -> Company:
        clean_name = normalize_name(name)
        clean_cnpj = normalize_cnpj(cnpj)
        company = Company(name=clean_name, cnpj=clean_cnpj, user_id=user_id)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def get_for_user(self, company_id: int, user_id: int) -> Company | None:
        return (
            self.db.query(Company)
            .filter(Company.id == company_id, Company.user_id == user_id)
            .first()
        )

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

    def list_by_user(self, user_id: int) -> list[Company]:
        return (
            self.db.query(Company)
            .filter(Company.user_id == user_id)
            .order_by(Company.name)
            .all()
        )
