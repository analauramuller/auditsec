# AuditaSecIFC

Ferramenta web para diagnostico de conformidade **NBR ISO/IEC 27001** (via **27002:2022**, 93 controles) e **NBR ISO/IEC 27701:2026** (Anexos A1 e A2, 49 controles).

## Funcionalidades

- Modulos 27001 e 27701 com perguntas em PT-BR
- Empresa unica por nome ou CNPJ
- Auditoria paginada com validacao por pagina
- Nova auditoria para empresa ja cadastrada (comparativo das 3 ultimas)
- Dashboard, relatorios HTML e comparativo por modulo

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL (`auditasecifc`)
- Frontend: Vue 3, Vite, Tailwind CSS, Chart.js
- Deploy: Docker Compose

## Subir com Docker

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- Web: http://localhost:5173

> Se voce alterou o catalogo de controles, use `docker compose down -v` para recriar o banco ou rode `python -m app.seed` para sincronizar titulos.

## Desenvolvimento local

### Backend

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export DATABASE_URL=postgresql://auditasec:auditasec_secret@localhost:5432/auditasecifc
alembic upgrade head
python scripts/generate_seeds.py   
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend && npm install && npm run dev
```

### Regenerar seeds

```bash
cd backend && python scripts/generate_seeds.py && python -m app.seed
```


## Integrantes do Projeto
Ana Laura da Silva Müller
Henrique Costa Nascimento
Sara de Almeida Sehnem
