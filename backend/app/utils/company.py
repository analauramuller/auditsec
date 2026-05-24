import re


def normalize_cnpj(cnpj: str | None) -> str | None:
    if not cnpj or not str(cnpj).strip():
        return None
    digits = re.sub(r"\D", "", cnpj)
    if len(digits) != 14:
        return None
    return digits


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())
