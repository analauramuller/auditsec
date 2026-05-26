import json
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.entities import AuditResponse, Control, User
from app.utils.password import validate_password

SEEDS_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"
SEED_FILES = ("iso27002_2022.json", "iso27701.json")


def load_seed_file(filename: str) -> list[dict]:
    return json.loads((SEEDS_DIR / filename).read_text(encoding="utf-8"))


def sync_catalog(db: Session) -> tuple[int, int]:
    inserted = 0
    updated = 0
    for filename in SEED_FILES:
        items = load_seed_file(filename)
        module = items[0]["module"] if items else None
        seed_codes = {item["code"] for item in items}

        for item in items:
            existing = (
                db.query(Control)
                .filter(Control.module == item["module"], Control.code == item["code"])
                .first()
            )
            if existing:
                existing.title = item["title"]
                existing.category = item["category"]
                existing.catalog_version = item["catalog_version"]
                existing.guidance_ref = item.get("guidance_ref")
                existing.description = item.get("description")
                updated += 1
            else:
                db.add(
                    Control(
                        module=item["module"],
                        code=item["code"],
                        title=item["title"],
                        category=item["category"],
                        catalog_version=item["catalog_version"],
                        guidance_ref=item.get("guidance_ref"),
                        description=item.get("description"),
                    )
                )
                inserted += 1

        if module:
            obsolete = (
                db.query(Control)
                .filter(Control.module == module, Control.code.notin_(seed_codes))
                .all()
            )
            for ctrl in obsolete:
                has_responses = (
                    db.query(AuditResponse).filter(AuditResponse.control_id == ctrl.id).count() > 0
                )
                if not has_responses:
                    db.delete(ctrl)

    db.commit()
    return inserted, updated


def ensure_admin_user(db: Session) -> User:
    login = settings.admin_login.strip()
    password = settings.admin_password
    validate_password(password)

    existing = (
        db.query(User).filter(func.lower(User.login) == login.lower()).first()
    )
    if existing:
        existing.login = login
        existing.password = password
        db.commit()
        return existing

    user = User(login=login, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main():
    db = SessionLocal()
    try:
        ensure_admin_user(db)
        inserted, updated = sync_catalog(db)
        print(f"Catalogo sincronizado: {inserted} novos, {updated} atualizados.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
