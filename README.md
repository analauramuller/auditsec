# 🔐 AuditaSecIFC

O **AuditaSecIFC** é uma ferramenta web desenvolvida para auxiliar no **diagnóstico de conformidade em Segurança da Informação e Privacidade**, com base nas normas **NBR ISO/IEC 27001** e **NBR ISO/IEC 27701**.

A ideia do projeto é permitir que auditores realizem avaliações de forma simples e organizada, registrando respostas para cada controle, acompanhando indicadores de conformidade e comparando auditorias realizadas ao longo do tempo.

---

## 🎯 Objetivo

O sistema foi criado para auxiliar organizações e auditores no levantamento estruturado da postura de segurança e privacidade, oferecendo:

- Avaliação baseada na **ISO/IEC 27002:2022** (93 controles para a ISO 27001);
- Avaliação baseada na **ISO/IEC 27701:2026** (49 controles dos anexos A1 e A2);
- Cálculo automático dos indicadores de conformidade;
- Dashboard com gráficos e estatísticas;
- Comparação entre auditorias anteriores;
- Geração de relatórios em HTML.

---

## ✨ Funcionalidades

### 🔑 Autenticação

- Cadastro de usuários;
- Login para acesso ao sistema.

### 📚 Módulos de auditoria

O auditor pode escolher entre:

- **ISO 27001** → 93 controles da ISO 27002:2022;
- **ISO 27701** → 49 controles dos anexos A1 e A2.

### 🏢 Cadastro de empresas

- Cadastro por nome ou CNPJ;
- Reutilização da empresa em novas auditorias;
- Histórico de auditorias armazenado.

### 📝 Wizard de auditoria

As perguntas são exibidas de forma paginada.

Cada controle pode ser respondido como:

- ✅ Conforme
- ❌ Não conforme
- 🔄 Em andamento
- ➖ Não aplica

Além disso:

- Existe validação por página;
- Não é possível finalizar a auditoria sem responder todos os controles.

### 📊 Dashboard

O sistema apresenta:

- Percentual geral de conformidade;
- Percentual por categoria de controle;
- Gráficos de pizza;
- Gráficos de barras;
- Indicadores de não conformidade e itens em andamento.

> Os controles marcados como **Não Aplica (N/A)** não entram no cálculo da conformidade.

### 📈 Comparativo

É possível comparar as **3 últimas auditorias finalizadas** de uma empresa para o mesmo módulo.

São exibidos:

- Tabela comparativa;
- Percentuais de evolução;
- Gráfico de evolução histórica.

### 📄 Relatórios

Disponíveis somente após a conclusão da auditoria.

Tipos:

- Relatório completo;
- Relatório agrupado por categoria;
- Modo atual;
- Modo comparativo.

---

## 🏗️ Arquitetura

```text
┌─────────────┐     HTTP/JSON      ┌─────────────┐     SQL      ┌────────────┐
│  Frontend   │ ◄────────────────► │   Backend   │ ◄──────────► │ PostgreSQL │
│    Vue 3    │                    │   FastAPI   │              │            │
│  Chart.js   │                    │ SQLAlchemy  │              │            │
└─────────────┘                    └─────────────┘              └────────────┘
```

---

## 🛠️ Stack utilizada

### Frontend

- Vue 3
- Vite
- Vue Router
- Pinia
- Tailwind CSS
- Chart.js

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- Jinja2
- Matplotlib

### Banco de dados

- PostgreSQL 16

### Infraestrutura

- Docker Compose

---

## 🗄️ Modelo de dados

As principais entidades do sistema são:

| Entidade | Descrição |
|----------|-----------|
| User | Usuário autenticado |
| Company | Empresa auditada |
| Control | Catálogo de controles |
| Audit | Auditoria realizada |
| AuditResponse | Respostas dos controles |

---

## 📏 Regras de negócio

1. A conformidade é calculada por:

```text
Conformidade (%) = Controles conformes ÷ (Total de controles - Não aplica) × 100
```

2. Uma auditoria só pode ser finalizada se todos os controles forem respondidos;

3. Relatórios ficam indisponíveis para auditorias em andamento;

4. O comparativo considera no máximo as 3 últimas auditorias finalizadas;

5. Os controles são agrupados conforme:
   - ISO 27002:2022 para a 27001;
   - Anexos A1 e A2 para a 27701.

---

## 🔄 Fluxo principal

O fluxo de utilização do **AuditaSecIFC** foi projetado para ser simples e intuitivo. O auditor inicia realizando o login, escolhe o módulo de auditoria desejado, seleciona ou cadastra uma empresa e, em seguida, responde aos controles por meio do wizard de auditoria. Após a finalização, os resultados ficam disponíveis no dashboard, no comparativo entre auditorias e nos relatórios.

### Diagrama do fluxo principal

<img width="738" height="1307" alt="activity-diagram-AuditSecIFC" src="https://github.com/user-attachments/assets/4455d0f2-4876-407c-9573-25f681e8515e" />

---

## 📚 Documentação UML

Para facilitar a compreensão da estrutura e do funcionamento do sistema, foi elaborado o diagrama de Classes abaixo.

<img width="727" height="513" alt="class-diagram-AuditSecIFC" src="https://github.com/user-attachments/assets/13d79674-6a4a-44a3-9e07-425a958ce6a0" />


---

## 🚀 Executando com Docker

```bash
cp .env.example .env

docker compose up --build
```

A aplicação ficará disponível em:

- API: http://localhost:8000
- Frontend: http://localhost:5173

> Caso o catálogo de controles seja alterado, execute:

```bash
docker compose down -v
```

ou

```bash
python -m app.seed
```

para sincronizar os dados.

---

## 💻 Desenvolvimento local

### Backend

```bash
cd backend

python3 -m venv .venv

.venv/bin/pip install -r requirements.txt

export DATABASE_URL=postgresql://auditasec:auditasec_secret@localhost:5432/auditasecifc

alembic upgrade head

python scripts/generate_seeds.py

python -m app.seed

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## 🌱 Regenerar os controles (Seeds)

```bash
cd backend

python scripts/generate_seeds.py

python -m app.seed
```

---

## 👨‍💻 Integrantes

- Ana Laura da Silva Müller
- Henrique Costa Nascimento
- Sara de Almeida Sehnem
