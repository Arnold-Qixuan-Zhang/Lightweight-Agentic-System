# Agentic AI Demo

A lightweight full-stack demonstration of an agentic AI system. Users submit a text instruction through a React web UI. A Python (FastAPI) backend uses **Groq** (native tool calling) and a small **LangGraph** loop to pick and run tools, then stores history and returns a step-by-step execution trace.

## Features

- **React frontend** — instruction box, execution trace, task history
- **Python backend (FastAPI)** — REST API with a LangGraph agent
- **Groq LLM** — `openai/gpt-oss-20b` with native tool calling (not keyword matching)
- **Multi-step tools** — up to 3 tool calls per request (one tool per step)
- **Three tools:**
  - `TextProcessorTool` — uppercase, lowercase, or word count
  - `CalculatorTool` — basic arithmetic (`+`, `-`, `*`, `/`)
  - `WeatherMockTool` — mock weather for a city (no external weather API)
- **Out-of-scope replies** — friendly message (HTTP 200), not an error
- **JSON history** — `backend/data/history.json` with export

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI app and routes
│   ├── requirements.txt
│   ├── .env.example            # Copy to .env and add GROQ_API_KEY
│   ├── agent/
│   │   ├── controller.py       # Runs the graph and saves history
│   │   ├── graph.py            # LangGraph: reason → execute → reason
│   │   ├── lc_tools.py         # LangChain wrappers around local tools
│   │   └── state.py
│   ├── llm/
│   │   ├── config.py           # GROQ_API_KEY / GROQ_MODEL
│   │   └── groq_client.py      # ChatGroq + bind_tools
│   ├── tools/
│   │   ├── text_processor.py
│   │   ├── calculator.py
│   │   └── weather_mock.py
│   ├── storage/
│   │   └── history_store.py
│   ├── models/
│   │   └── schemas.py
│   └── data/
│       └── history.json
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── api/client.js
│   └── package.json
│
└── README.md
```

## Prerequisites

- **Anaconda** or **Miniconda**
- **Node.js 18+** and **npm**
- A **Groq API key** ([console.groq.com](https://console.groq.com))

Verify:

```bash
conda --version
node --version
npm --version
```

## Setup

### 1. Backend

```bash
cd backend
```

Create and activate a Conda environment:

```bash
conda create -n agentic-demo python=3.11 -y
conda activate agentic-demo
pip install -r requirements.txt
```

Configure Groq (required):

```bash
copy .env.example .env
```

On macOS/Linux use `cp .env.example .env`. Edit `.env` and set:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit `.env`. `.env.example` has no secret.

### 2. Frontend

In a **second** terminal:

```bash
cd frontend
npm install
```

## Running the Application

### Terminal 1 — Backend

```bash
cd backend
conda activate agentic-demo
uvicorn main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`, enter an instruction, click **Run**.

## How the Agent Works

1. **Received** — the instruction is stored in the trace.
2. **Reason (Groq)** — the model may emit a native **tool call** or a plain-text reply.
3. **Execute** — the matching local tool runs (`execute()` only). Extra parallel tool calls in the same turn are deferred (one tool per step).
4. **Reason again** — Groq sees the tool result and either calls another tool (max 3) or finishes.
5. **Out of scope** — no tool is called; the API returns HTTP 200 with a short explanation.
6. The run is saved to `backend/data/history.json`.

## Example Instructions

| Instruction | What happens |
|-------------|--------------|
| `convert hello world to uppercase` | TextProcessorTool → `HELLO WORLD` |
| `make this shouty: hello` | Same tool, natural wording |
| `count words in the quick brown fox` | Word count |
| `what’s 15 times 4` | CalculatorTool → `60` |
| `is it raining in Toronto?` | WeatherMockTool (mock data) |
| `uppercase hello then count the words` | Two tool calls, then a short summary |
| `tell me a joke` | No tool; friendly “I can only help with…” message |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tasks` | Run the agent (always 200 for in-scope and out-of-scope) |
| `GET` | `/api/history` | Recent history |
| `GET` | `/api/history/export` | Download `history.json` |
| `GET` | `/api/health` | Health check |

HTTP 500 is reserved for missing `GROQ_API_KEY` or Groq/server failures — not for jokes or unknown tasks.

### Example: Submit a task via curl

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d "{\"instruction\": \"convert hello to uppercase\"}"
```

## Troubleshooting

**`GROQ_API_KEY is not set`**

- Copy `backend/.env.example` to `backend/.env` and paste your key.
- Restart uvicorn after changing `.env`.

**`conda: command not found`**

- Use **Anaconda Prompt**, or run `conda init powershell` and restart PowerShell.

**Conda environment not activating**

```bash
conda env list
conda activate agentic-demo
pip install -r requirements.txt
```

**`ModuleNotFoundError`**

- Run uvicorn from `backend/`.
- Activate `agentic-demo` and reinstall: `pip install -r requirements.txt`

**Frontend cannot reach the backend**

- Backend on port `8000`, frontend on `5173`.
- CORS is allowed for `http://localhost:5173`.

**Port already in use**

- Backend: `uvicorn main:app --reload --port 8001` (update `API_BASE` in `frontend/src/api/client.js`).
- Frontend: `npm run dev -- --port 5174`

**History file missing**

- Created automatically at `backend/data/history.json` on the first task.

## Building for Production (optional)

```bash
cd frontend
npm run build

cd ../backend
conda activate agentic-demo
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Future Improvements
- Retry, error-handling, fallback components in the system to make it more robust.
- Cache management for larger traffic.