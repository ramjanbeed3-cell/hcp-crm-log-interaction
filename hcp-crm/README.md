# AI-First CRM — HCP Module: Log Interaction Screen

A working prototype of the **Log Interaction Screen** for a Healthcare Professional
(HCP) CRM module, built for field representatives. It supports logging an
interaction either via a **structured form** or a **conversational chat interface**,
backed by a **LangGraph** agent running on **Groq**.

---

## 1. Architecture Overview

```
frontend/   React 18 + Redux Toolkit (Log Interaction Screen: form + chat modes)
backend/    FastAPI (REST API) + LangGraph agent + SQLAlchemy (Postgres/MySQL)
```

- **Frontend (React + Redux):** `LogInteractionScreen` toggles between
  `StructuredForm` and `ChatInterface`. Redux slices (`interactionsSlice`,
  `chatSlice`) hold HCP list, selected HCP context, logged interactions, and
  chat history; async thunks call the FastAPI backend via axios.
- **Backend (FastAPI):** exposes REST endpoints for HCPs/interactions
  (used by the structured form) and a `/api/chat` endpoint that drives the
  LangGraph agent (used by the chat interface). Both paths ultimately call
  the same underlying tools, so data logged via either mode is consistent.
- **Database:** SQLAlchemy models work against either **Postgres** or
  **MySQL** — just change `DATABASE_URL` in `.env` (see below). Tables:
  `hcps`, `interactions`, `followups`.
- **LLMs (Groq):** primary model `gemma2-9b-it` drives the fast tool-calling
  loop; `llama-3.3-70b-versatile` is used as a fallback / for heavier
  synthesis tasks (report generation, malformed-JSON retries).

---

## 2. The Role of the LangGraph Agent

The LangGraph agent is the reasoning layer sitting between the rep's natural
language and the CRM's structured data model. Concretely, it:

1. **Interprets free-text/chat input** ("Just saw Dr. Rao, she liked the new
   dosing data but wants to see phase 3 numbers before prescribing") and
   decides *which* CRM action that maps to (a new log, an edit, a follow-up,
   a report request).
2. **Grounds itself in CRM state** before acting — e.g. it calls
   `fetch_hcp_profile` to pull the HCP's history so it doesn't log a new
   interaction blind, or so it can reference the right interaction when the
   rep says "update what I just logged."
3. **Extracts structured fields from unstructured text** — sentiment,
   products discussed, key entities/objections — via the LLM, and persists
   them through tool calls rather than the LLM writing to the DB directly
   (keeps the agent auditable and the DB writes deterministic/testable).
4. **Chains multiple tool calls in one turn** when needed — e.g. log an
   interaction *and* schedule a follow-up in a single message — using
   LangGraph's tool-calling loop (`agent -> tools -> agent -> ...`) rather
   than a single fixed function-call.
5. **Reports back conversationally**, translating tool JSON results into
   plain language confirmations for the rep.

### Graph shape

```
START -> agent (Groq LLM bound to 5 tools)
           |
           |-- tool call requested? --> tools (ToolNode executes it) --> agent
           |
           +-- no tool call --> END (final reply returned to the UI)
```

## 3. The 5 LangGraph Tools

| Tool | Purpose |
|---|---|
| **`log_interaction`** | Captures a new interaction. Takes the rep's raw text (from chat, or the concatenated structured-form fields), calls the LLM to produce a short summary, extract entities (products, objections, commitments) and classify sentiment, then persists a new `Interaction` row. |
| **`edit_interaction`** | Modifies a previously logged interaction (type, products, notes, sentiment). If `notes` changes, the summary is regenerated via the LLM so the AI summary never goes stale relative to the underlying text. |
| **`fetch_hcp_profile`** | Retrieves an HCP's profile plus their N most recent interactions — used to ground the agent with context before it logs or edits anything. |
| **`schedule_followup`** | Creates a follow-up task tied to a given interaction, with a due date and reason (e.g. "send updated dosing study in 7 days"). |
| **`generate_summary_report`** | Aggregates an HCP's interaction history over a lookback window into an LLM-synthesized report — trends, sentiment trajectory, open items — useful before a next visit. |

Full implementations: `backend/app/agent/tools.py`.
Graph wiring: `backend/app/agent/graph.py`.

### Log Interaction — detail

`log_interaction(hcp_id, raw_text, interaction_type, rep_id)`:
1. Loads the HCP record (fails clearly if not found).
2. Sends `raw_text` to the Groq LLM with a prompt asking for JSON:
   `summary`, `products_discussed`, `sentiment`, `entities`.
3. If the small model (`gemma2-9b-it`) returns malformed JSON, retries once
   against the fallback model (`llama-3.3-70b-versatile`).
4. Writes a new `Interaction` row with both the raw text (`notes`,
   `raw_transcript`) and the AI-derived fields (`ai_summary`, `ai_entities`,
   `sentiment`), and returns the new record as JSON.

### Edit Interaction — detail

`edit_interaction(interaction_id, updates)`:
1. Loads the existing `Interaction` (fails clearly if not found).
2. Applies whichever of `interaction_type`, `products_discussed`, `notes`,
   `sentiment` are present in the `updates` JSON.
3. If `notes` was part of the update, re-summarizes via the LLM so the
   summary reflects the edit.
4. Persists and returns the updated record.

---

## 4. Running It Locally

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: set DATABASE_URL (Postgres or MySQL) and GROQ_API_KEY
uvicorn app.main:app --reload --port 8000
```

Postgres example (local, via Docker):
```bash
docker run -d --name hcp-crm-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hcp_crm -p 5432:5432 postgres:16
```

Get a Groq API key at https://console.groq.com/keys and paste it into
`GROQ_API_KEY` in `.env`. Models used: `gemma2-9b-it` (primary) and
`llama-3.3-70b-versatile` (fallback), both already set as defaults in
`.env.example`.

Seed a couple of HCPs to try the demo (simple curl, or use `/docs`):
```bash
curl -X POST http://localhost:8000/api/hcps \
  -H "Content-Type: application/json" \
  -d '{"name": "Dr. Anjali Rao", "specialty": "Cardiology", "hospital": "City General"}'
```

FastAPI interactive docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm start
```

App runs at http://localhost:3000 and talks to the backend at
`http://localhost:8000` (override with `REACT_APP_API_BASE` env var).

---

## 5. Tech Stack Recap

- **Frontend:** React 18, Redux Toolkit, axios, Google Inter font.
- **Backend:** Python, FastAPI, SQLAlchemy.
- **AI Agent Framework:** LangGraph (`langgraph`), via `langchain-groq`.
- **LLMs:** Groq — `gemma2-9b-it` (primary), `llama-3.3-70b-versatile` (fallback/synthesis).
- **Database:** Postgres or MySQL (swap via `DATABASE_URL`).

---

## 6. Notes / Assumptions

- Auth/multi-tenant rep login is out of scope for this prototype; `rep_id`
  defaults to `"rep_demo"`.
- Tables are auto-created on startup (`Base.metadata.create_all`) for ease
  of grading/demo; a real deployment would use Alembic migrations.
- The structured form and the chat interface both route through the same
  `log_interaction` tool under the hood, so data is consistent regardless
  of which mode a rep uses.
