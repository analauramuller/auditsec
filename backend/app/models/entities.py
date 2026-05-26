from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.domain.enums import AuditStatus, IsoModule, ResponseStatus


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(18))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    audits: Mapped[list["Audit"]] = relationship(back_populates="company")


class Control(Base):
    __tablename__ = "controls"

    id: Mapped[int] = mapped_column(primary_key=True)
    module: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    catalog_version: Mapped[str] = mapped_column(String(50), nullable=False)
    guidance_ref: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("module", "code", name="uq_control_module_code"),)

    responses: Mapped[list["AuditResponse"]] = relationship(back_populates="control")


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    module: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    audit_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=AuditStatus.DRAFT.value)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="audits")
    responses: Mapped[list["AuditResponse"]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )


class AuditResponse(Base):
    __tablename__ = "audit_responses"

    id: Mapped[int] = mapped_column(primary_key=True)
    audit_id: Mapped[int] = mapped_column(ForeignKey("audits.id"), nullable=False)
    control_id: Mapped[int] = mapped_column(ForeignKey("controls.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    work_in_progress: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("audit_id", "control_id", name="uq_audit_control"),)

    audit: Mapped["Audit"] = relationship(back_populates="responses")
    control: Mapped["Control"] = relationship(back_populates="responses")
