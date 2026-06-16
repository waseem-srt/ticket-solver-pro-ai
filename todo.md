# Project Setup & Troubleshooting TODO List

This document outlines the steps and exact commands you need to run to fix the database connection issues, start the FastAPI backend correctly, and configure local models.

---

## 1. Database Setup (Completed ✅)

You successfully spun up the PostgreSQL database container:
```powershell
docker compose -f docker/docker-compose.yml up -d postgres
```

---

## 2. Initialize the Database and Seed Admin User (Completed ✅)

* **Migrations & Seeding Run**: I created the initial database migration revision, applied the migration script, and successfully executed `seed_admin.py` to populate the `users` table with the initial administrator: `admin@platform.local` / `Admin@1234`.
* **Fix Applied**: I fixed a relationship mapping bug in `backend/models/user.py` where the `user_id` mapped column was missing the `ForeignKey("users.id")` constraint. I also removed print emojis from the scripts to ensure they run cleanly on Windows consoles without codec/character errors.

---

## 3. Load datasets (Completed ✅)

* **Hugging Face Loader Implemented & Run**: I modified the loading script to automatically fall back to downloading and loading the **[mindweave/help-desk-tickets](https://huggingface.co/datasets/mindweave/help-desk-tickets)** dataset directly from Hugging Face if no local CSV files exist.
* **Database Import Complete**: I executed the script which downloaded 1,000 synthetic help-desk tickets, normalized priorities/statuses/categories, and successfully committed them to your PostgreSQL database!

---

## 4. Run the FastAPI Backend Correctly

Your error: `Error loading ASGI app. Could not import module "main"` happened because you ran `uvicorn` from the root directory instead of the `backend` folder where `main.py` is located.

Run the following commands:

```powershell
# Navigate to the backend directory where main.py resides
cd C:\Users\mubee\Desktop\TechMahindra\backend

# Start the uvicorn server
uvicorn main:app --reload
```
*Alternatively, you can run it from the root directory using the `--app-dir` argument:*
```powershell
# From C:\Users\mubee\Desktop\TechMahindra
uvicorn main:app --reload --app-dir backend
```
* **Dependency Fix Applied**: I installed `email-validator` in your virtual environment. This library is required by Pydantic for the `EmailStr` field type in registration requests, which previously crashed the ASGI server startup. I have also added it to `backend/requirements.txt`.

---

## 5. Chat Agent Pipeline (Completed ✅)

* **Fix Applied**: I resolved the LangGraph startup exception: `langgraph.errors.InvalidUpdateError: Must write to at least one of []` that crashed chat queries.
* **The Cause**: The python class `AgentState` in `backend/agents/nodes.py` was inheriting from standard `dict` instead of inheriting from `TypedDict`. As a result, LangGraph was unable to detect any state channels/keys, throwing errors when nodes tried to output state changes.
* **The Resolution**: I imported and changed `AgentState` to inherit from `TypedDict` and annotated its keys with proper types. The pipeline now executes and responds successfully.

---

## 6. Running the Frontend

```powershell
# Open a new PowerShell window, navigate to frontend and start the development server
cd C:\Users\mubee\Desktop\TechMahindra\frontend
npm run dev
```

---

## 7. Local Model Management & Persistence

### The Embedding Model (`BAAI/bge-small-en-v1.5`)
* **Is it downloaded every time?** No. The embedding model is cached locally on your disk in `C:\Users\mubee\.cache\huggingface\hub/` after the first download. It does not download again.
* **Is it loaded forever?** No, RAM is volatile. When the backend Python server is stopped, the model is unloaded from RAM. When you start the server again, it loads the model from your local disk cache into RAM (which takes a few seconds).
* **Running completely offline**: If you want to prevent HuggingFace from even checking online for updates, set this environment variable in your terminal before launching the backend:
  ```powershell
  $env:HF_HUB_OFFLINE=1
  ```

### The LLM Model (Local PyTorch/Transformers Option Added! 🎉)
* **API Option (Default)**: The app queries `unsloth/Llama-3.1-8B-Instruct` via the remote HuggingFace Serverless Inference API (requires internet connection and `HF_TOKEN` in your `.env` file).
* **Local Option (Downloaded locally once)**: I have added a local execution pathway using your Python environment's PyTorch/transformers libraries.
  To download and run the model locally on your machine:
  1. Open your `.env` file and add:
     ```env
     RUN_LOCAL_LLM=true
     ```
  2. *(Optional)* Llama-3.1-8B is very large (16GB) and runs slowly on most CPUs. If you want a fast, lightweight local model that runs easily on CPUs, change the model repo in your `.env` file:
     ```env
     HF_MODEL_REPO=Qwen/Qwen2.5-1.5B-Instruct
     ```
     *(Note: `Qwen/Qwen2.5-1.5B-Instruct` is open source, requires no login/agreement, downloads once to your machine, and performs exceptionally well on CPUs).*
  3. When you start your backend server (`uvicorn main:app --reload`), it will automatically download the model from Hugging Face on the first run and cache it in `C:\Users\mubee\.cache\huggingface\hub/`. From then on, it will load it locally from disk cache and run it entirely offline.
