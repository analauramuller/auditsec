import enum


class IsoModule(str, enum.Enum):
    ISO27001 = "ISO27001"
    ISO27701 = "ISO27701"


class ControlCategory(str, enum.Enum):
    ORGANIZATIONAL = "organizational"
    PEOPLE = "people"
    PHYSICAL = "physical"
    TECHNOLOGICAL = "technological"
    PRIVACY = "privacy"


class AuditStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class ResponseStatus(str, enum.Enum):
    CONFORME = "CONFORME"
    NAO_CONFORME = "NAO_CONFORME"
    NAO_APLICA = "NAO_APLICA"
    EM_ANDAMENTO = "EM_ANDAMENTO"
