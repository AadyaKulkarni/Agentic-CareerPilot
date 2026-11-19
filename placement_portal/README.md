# Placement Readiness & Career Intelligence Portal

A production-oriented starter for a student placement/career intelligence platform.

## Stack
- Frontend: React + TypeScript + Vite + Tailwind CSS + Recharts
- Backend: FastAPI + SQLAlchemy + JWT
- Database: PostgreSQL
- Cache/queue-ready: Redis
- ML: scikit-learn rule/feature-based career-fit engine (replaceable by trained models)
- LLM: provider abstraction with OpenAI-compatible HTTP support and secure server-side API keys

## Quick start with Docker
1. Install Docker Desktop.
2. Copy `.env.example` to `.env` and update secrets if needed.
3. Run `docker compose up --build`.
4. Open http://localhost:5173.
5. API docs: http://localhost:8000/docs

## Local development
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## LLM keys
The app supports a user-level LLM configuration from Settings. Keys are accepted by the backend only and encrypted at rest using `SECRET_KEY`. Do not put user keys in frontend code.

The included `.env` intentionally contains empty LLM keys. Add your own key through the UI or environment variables for development.


## AI agents (matches the project brief)

| Agent | What it does | Code |
|---|---|---|
| **Resume Agent** | Upload PDF/DOCX/TXT, extract contact, education, skills, projects, experience; ATS-style score (100 pts) with concrete fixes; optionally merges findings into your profile without overwriting your entries | `backend/app/agents/resume_agent.py` |
| **Skill Gap Agent** | Compares skills evidence (profile + resume + projects + coding) with role requirements; prioritised gap report, effort estimates, closest alternative roles | `skill_gap_agent.py`, role data in `catalog.py` |
| **Coding Analytics Agent** | Fetches public stats from LeetCode, Codeforces and GitHub (or manual entry); coding score, difficulty mix, strengths/gaps, recommendations | `coding_agent.py` |
| **Job Matching Agent** | Ranks companies/roles using skill coverage, TF-IDF profile similarity, DSA fit and CGPA; matches pasted job descriptions | `job_agent.py`, data in `app/data/companies.json` |
| **Interview Agent** | Mock interview (HR, technical, project, behavioural) from your role/skills/projects; LLM evaluation if a key is configured, otherwise keyword + STAR-structure scoring | `interview_agent.py` |

### Expected outputs
- **Placement readiness score** (`GET /api/readiness`): transparent weighted blend (profile 8, academics 10, skills 24, portfolio 10, resume 13, coding 20, interview 15). Areas not yet assessed count as zero and are flagged, so the score cannot look better than the evidence.
- **Skill-gap report** (`GET /api/skills/gap?target_role=`)
- **Company / role matches** (`GET /api/companies/matches`, `GET /api/jobs/live`, `POST /api/job/match`)
- **Learning roadmap** (`POST /api/roadmap/generate`): week-by-week plan from gaps in every agent, shown on the Learning Roadmap page.

### New API endpoints
`POST /resume/parse` (multipart) · `POST /resume/analyze-text` · `GET /resume/latest` · `GET /skills/gap` · `GET /roles` · `POST /coding/sync` · `POST /coding/manual` · `GET /coding/analytics` · `DELETE /coding/{platform}` · `GET /companies/matches` · `POST /job/match` · `POST /interview/start` · `POST /interview/{id}/answer` · `POST /interview/{id}/finish` · `GET /interview/sessions` · `GET /interview/{id}` · `GET /readiness` · `POST /roadmap/generate`

### Notes and limits
- **Embeddings:** similarity uses TF-IDF (offline, no key). `agents/similarity.py` is the single place to swap in neural embeddings.
- **Company catalog is illustrative.** Cut-offs and hiring processes are approximations; edit `app/data/companies.json` for your campus drives.
- **Coding platforms:** the backend calls LeetCode (unofficial GraphQL), Codeforces and GitHub public APIs. LeetCode's endpoint is unofficial and may change or rate-limit; manual entry is the fallback.
- **LLM providers:** OpenAI, Gemini and Anthropic (Settings page). Without a key the Interview Agent uses its offline question bank and heuristic scoring; heuristics reward keyword coverage and cannot verify correctness.
- **Database:** new tables (`resume_analyses`, `coding_stats`, `interview_sessions`, `readiness_snapshots`) are created automatically on startup. No existing table was changed, so no migration is needed.

### Tests
```bash
cd backend && python -m unittest discover -s tests -v
```

## Demo account
The backend exposes registration. Create your own account from the UI.

## Agentic AI additions (Agentic AI Lab)

The updated build adds a sidebar page named **Agentic AI Lab** (`/agentic-lab`) and authenticated API endpoints:

- `GET /api/agentic/status` — lists the agents, registered tools, RAG method, memory design, and MCP endpoint.
- `POST /api/agentic/run` — runs a transparent workflow: read the signed-in student's profile → run Skill Gap analysis → retrieve relevant career guidance → return a combined recommendation and execution trace.
- `POST /api/agentic/rag/query` — retrieves relevant passages from the bundled career knowledge base using TF-IDF and returns the retrieved source titles. This is a local, deterministic RAG retrieval demo; the response synthesis does not require an external LLM.
- `POST /api/agentic/tools/call` — invokes one of the allow-listed application tools.
- `GET/POST/DELETE /api/agentic/memory` — views, stores, or clears Short-Term Memory (STM) and Task Memory (TM). **These memories are in-process and reset when the backend restarts.** They are isolated by logged-in user ID.
- `POST /api/mcp` — a lightweight MCP-style JSON-RPC HTTP tool endpoint supporting `initialize`, `ping`, `tools/list`, and `tools/call`. Send the normal bearer token from login in the `Authorization` header. Tools are allow-listed and read-only.

### MCP test request

Send a POST request to `http://localhost:8000/api/mcp` with `Content-Type: application/json`, `Authorization: Bearer <access_token>`, and this body:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

To call a tool:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_career_knowledge","arguments":{"query":"backend developer skills"}}}
```

### Scope and honest limitations

- The existing Resume, Skill Gap, Coding Analytics, Job Matching, and Interview agent modules remain in place. The Agentic AI Lab exposes a new orchestrated workflow and trace so the sequence can be demonstrated.
- RAG uses a small bundled knowledge set and TF-IDF retrieval, not a hosted vector database. Expand `CAREER_DOCS` in `backend/app/api/agentic.py` to add curated materials.
- MCP support is a lightweight HTTP JSON-RPC tool endpoint in this app, not a connector to an external MCP server. It exposes only the listed safe, read-only tools.
- STM/TM is implemented as in-memory demo state; use a database-backed store for durable memory in production.
- LLM calls still require a valid provider and API key in AI / LLM Settings. RAG and the demo agent workflow work without an LLM key.

### Run and test

From the project root:

```bash
docker compose up --build
```

Open `http://localhost:5173`, sign in, and select **Agentic AI Lab**. FastAPI docs are at `http://localhost:8000/docs`.

Run backend unit tests inside the backend environment with:

```bash
python -m unittest discover -s tests -v
```


### Live job discovery (Gemini/OpenAI analysis; no Adzuna)
- Live vacancies are retrieved from Remotive's public remote-jobs API. Remotive is the vacancy source; Gemini or OpenAI analyses the returned listings against the signed-in student's profile/resume. An LLM is not a vacancy database and must not be treated as a source of verified live openings.
- Adzuna has been removed. No Adzuna app ID or app key is needed.
- To enable AI explanations, add either `GEMINI_API_KEY` (recommended) or `OPENAI_API_KEY` to the project-root `.env`. Gemini is preferred if both are set. Defaults: `GEMINI_MODEL=gemini-2.5-flash` or `OPENAI_MODEL=gpt-4o-mini`.
- Without an AI key, live remote listings still load and CareerPilot uses its local skill-overlap scoring fallback.
- `GET /api/jobs/live?role=Software%20Developer&location=India&limit=30` retrieves real remote listings and ranks them against the student's profile/resume. The source is remote-focused and is not a comprehensive India on-site vacancy feed.
- Always apply through the original employer/job-board link and verify that the vacancy is still open.
- **Windows / VS Code setup:** Open the `placement_portal` folder, open `.env`, paste your Gemini key after `GEMINI_API_KEY=`, save, then run `docker compose up --build`. Open `http://localhost:5173`, sign in, choose Job Matching Agent → Live job vacancies. Do not put API keys in frontend files or commit them to GitHub.
- Get a Gemini API key from https://aistudio.google.com/app/apikey. The Gemini API has a free tier subject to Google's model, region and rate limits. OpenAI API keys are also supported, but ChatGPT subscriptions do not include API credits; API usage may be billed separately.

### Registration and login

- Open `/register` and create a new account with your name, email, password, and password confirmation.
- Registration creates the account and its empty student profile, then takes you to `/login` so you sign in explicitly.
- Email addresses are normalized to lowercase; attempting to register an existing email returns a clear conflict message.
- Passwords must contain at least 6 characters.
