# Ticket Solver Pro AI

A production-ready RAG-powered ticket solving platform with LangGraph agents, ChromaDB vector store, and HuggingFace LLM.

## Stack
- **Backend**: FastAPI + SQLAlchemy 2 (async) + Alembic + PostgreSQL
- **LLM**: `unsloth/Llama-3.1-8B-Instruct` via HuggingFace Inference API
- **RAG**: ChromaDB + BGE-small-en-v1.5 embeddings + LangGraph
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + Shadcn UI

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Docker & Docker Compose (optional)
- HuggingFace account with token

### 1. Copy environment files
```bash
cp .env.example .env
# Fill in your values: DATABASE_URL, JWT_SECRET_KEY, HF_TOKEN
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed admin user
python ../scripts/seed_admin.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Docker (all-in-one)
```bash
docker compose -f docker/docker-compose.yml up --build
```

### 5. Load datasets
Place CSV files in `data/tickets/` then:
```bash
python scripts/load_datasets.py
```

## Default Credentials
- Admin: `admin@platform.local` / `Admin@1234`

## API Docs
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
