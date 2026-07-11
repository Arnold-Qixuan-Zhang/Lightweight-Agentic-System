# Agentic AI Demo

A lightweight full-stack demonstration of an agentic AI system. Users submit a text instruction through a React web UI; a Python (FastAPI) backend routes the request to the appropriate tool, executes it, stores the history, and returns a step-by-step execution trace.

## Features

- **React frontend** — simple UI for entering instructions and viewing execution traces
- **Python backend (FastAPI)** — REST API with an agent controller and rule-based tool router
- **Three tools:**
  - `TextProcessorTool` — uppercase, lowercase, or word count
  - `CalculatorTool` — basic arithmetic (`+`, `-`, `*`, `/`)
  - `WeatherMockTool` — mock weather data for a city (no external API)
- **JSON history storage** — all tasks persisted to `backend/data/history.json` with export support

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI app and routes
│   ├── requirements.txt
│   ├── agent/
│   │   ├── controller.py       # Orchestrates the agent pipeline
│   │   └── router.py           # Selects the appropriate tool
│   ├── tools/
│   │   ├── text_processor.py
│   │   ├── calculator.py
│   │   └── weather_mock.py
│   ├── storage/
│   │   └── history_store.py    # JSON file persistence
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   └── data/
│       └── history.json        # Task history (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/         # UI components
│   │   └── api/client.js       # API client
│   └── package.json
│
└── README.md
```

## Prerequisites

- **Anaconda** or **Miniconda** (includes Python and `conda`)
- **Node.js 18+** and **npm**

Verify installations:

```bash
conda --version
node --version
npm --version
```

## Setup

### 1. Backend

Open a terminal (Anaconda Prompt on Windows works well) and navigate to the backend directory:

```bash
cd backend
```

Create and activate a Conda environment:

```bash
conda create -n agentic-demo python=3.11 -y
conda activate agentic-demo
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Frontend

Open a **second** terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
```

## Running the Application

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1 — Start the backend

```bash
cd backend
conda activate agentic-demo
uvicorn main:app --reload --port 8000
```

The API will be available at:

- API base: `http://localhost:8000`
- Interactive docs (Swagger): `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### Terminal 2 — Start the frontend

```bash
cd frontend
npm run dev
```

The UI will be available at:

- `http://localhost:5173`

Open that URL in your browser. Enter an instruction and click **Run** to see the agent trace.

## Example Instructions

Try these prompts in the UI:

| Instruction | Tool Selected | Expected Result |
|-------------|---------------|-----------------|
| `convert hello world to uppercase` | TextProcessorTool | `HELLO WORLD` |
| `convert Hello World to lowercase` | TextProcessorTool | `hello world` |
| `count words in the quick brown fox` | TextProcessorTool | `4` |
| `calculate 15 * 4` | CalculatorTool | `60` |
| `add 10 and 25` | CalculatorTool | `35` |
| `what is the weather in Toronto` | WeatherMockTool | Mock weather for Toronto |
| `weather in Vancouver` | WeatherMockTool | Mock weather for Vancouver |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tasks` | Submit an instruction and run the agent |
| `GET` | `/api/history` | List recent task history |
| `GET` | `/api/history/export` | Download full history as `history.json` |
| `GET` | `/api/health` | Health check |

### Example: Submit a task via curl

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d "{\"instruction\": \"convert hello to uppercase\"}"
```

Example response:

```json
{
  "task_id": "abc-123",
  "result": "HELLO",
  "trace": [
    { "step": 1, "message": "Received the input \"convert hello to uppercase\"" },
    { "step": 2, "message": "Selected tool: TextProcessorTool (operation: uppercase, text: hello)" },
    { "step": 3, "message": "Executed TextProcessorTool → HELLO" }
  ]
}
```

## How the Agent Works

1. **Step 1** — The controller receives the user's instruction.
2. **Step 2** — The router inspects the instruction with keyword/pattern matching and selects a tool.
3. **Step 3** — The selected tool parses parameters, executes, and returns a result.
4. The full record (instruction, tool, params, result, trace, timestamp) is saved to `backend/data/history.json`.

The UI displays each step in the **Execution Trace** panel. Past runs appear in the **History** panel; click any entry to re-view its trace. Use **Export History** to download the JSON file.

## Troubleshooting

**`conda: command not found`**

- Open **Anaconda Prompt** (Windows) or restart your terminal after installing Anaconda/Miniconda.
- On Windows, you can also run `conda init powershell` and restart PowerShell.

**Conda environment not activating**

```bash
conda env list                  # confirm agentic-demo exists
conda activate agentic-demo
```

If the environment does not exist yet, create it:

```bash
conda create -n agentic-demo python=3.11 -y
conda activate agentic-demo
pip install -r requirements.txt
```

**`ModuleNotFoundError` when starting the backend**

- Run `uvicorn` from inside the `backend/` directory.
- Ensure the Conda environment is activated (`conda activate agentic-demo`).
- Reinstall dependencies: `pip install -r requirements.txt`

**Frontend cannot reach the backend (CORS or network error)**

- Ensure the backend is running on port `8000`.
- Ensure the frontend is running on port `5173`.
- CORS is pre-configured for `http://localhost:5173`.

**Port already in use**

- Backend: `uvicorn main:app --reload --port 8001` (update `API_BASE` in `frontend/src/api/client.js` if you change the port).
- Frontend: `npm run dev -- --port 5174`

**History file missing**

- The file is auto-created at `backend/data/history.json` on the first task submission.

## Building for Production (optional)

```bash
# Frontend static build
cd frontend
npm run build

# Backend (production example)
cd backend
conda activate agentic-demo
uvicorn main:app --host 0.0.0.0 --port 8000
```

For this demo, running both dev servers locally is sufficient.
