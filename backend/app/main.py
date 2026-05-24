from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import audits, companies, controls, modules

app = FastAPI(
    title="AuditaSecIFC",
    description="Auditoria de conformidade NBR ISO/IEC 27001 e 27701 — IFC",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modules.router)
app.include_router(controls.router)
app.include_router(companies.router)
app.include_router(audits.router)


@app.get("/health")
def health():
    return {"status": "ok"}
