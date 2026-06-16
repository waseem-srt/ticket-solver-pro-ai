# 🎫 Ticket Solver Pro AI

> **Production-ready RAG-powered ticket solving platform with LangGraph agents, ChromaDB vector store, and HuggingFace LLM.**

---

## 🚀 Tech Stack

| Layer        | Technology                                                    |
| ------------ | ------------------------------------------------------------- |
| **Backend**  | FastAPI + SQLAlchemy 2 (async) + Alembic + PostgreSQL         |
| **LLM**      | `unsloth/Llama-3.1-8B-Instruct` via HuggingFace Inference API |
| **RAG**      | ChromaDB + BGE-small-en-v1.5 embeddings + LangGraph           |
| **Frontend** | Next.js 14 + TypeScript + Tailwind CSS + Shadcn UI            |

---

## ⚡ Quick Start

### Prerequisites

Before starting, ensure the following are installed:

* Python 3.11+
* Node.js 18+
* PostgreSQL 16+
* Docker & Docker Compose (optional)
* HuggingFace account with token

---

### 1️⃣ Copy Environment Files

```bash
cp .env.example .env

# Fill in your values:
# DATABASE_URL
# JWT_SECRET_KEY
# HF_TOKEN
```

---

### 2️⃣ Backend Setup

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

---

### 3️⃣ Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

### 4️⃣ Docker (All-in-One)

```bash
docker compose -f docker/docker-compose.yml up --build
```

---

### 5️⃣ Load Datasets

Place CSV files in:

```text
data/tickets/
```

Then run:

```bash
python scripts/load_datasets.py
```

---

## 🔐 Default Credentials

| Role  | Email                  | Password     |
| ----- | ---------------------- | ------------ |
| Admin | `admin@platform.local` | `Admin@1234` |

---

## 📚 API Documentation

| Documentation | URL                         |
| ------------- | --------------------------- |
| Swagger UI    | http://localhost:8000/docs  |
| ReDoc         | http://localhost:8000/redoc |

---

### ✅ Project Status

Ticket Solver Pro AI is a production-ready support automation platform powered by Retrieval-Augmented Generation (RAG), LangGraph agents, ChromaDB vector search, and HuggingFace-hosted LLMs.
