from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import audits, auth, companies, controls, modules
from app.auth import require_auth
from app.config import settings

app = FastAPI(
    title="AuditaSecIFC",
    description="Auditoria de conformidade NBR ISO/IEC 27001 e 27701 — IFC",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    session_cookie="auditasec_session",
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(modules.router, dependencies=[Depends(require_auth)])
app.include_router(controls.router, dependencies=[Depends(require_auth)])
app.include_router(companies.router, dependencies=[Depends(require_auth)])
app.include_router(audits.router, dependencies=[Depends(require_auth)])


@app.get("/health")
def health():
    return {"status": "ok"}
