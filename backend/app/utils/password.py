import re

from fastapi import HTTPException


PASSWORD_LETTER_RE = re.compile(r"[A-Za-z]")


def validate_password(password: str) -> None:
    if password is None:
        raise HTTPException(400, "Senha obrigatoria.")
    if len(password) < 4 or len(password) > 12:
        raise HTTPException(400, "Senha deve ter entre 4 e 12 caracteres.")
    if not PASSWORD_LETTER_RE.search(password):
        raise HTTPException(400, "Senha deve conter ao menos uma letra.")

