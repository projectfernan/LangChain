# LangChain Demo App

A full-stack LangChain demo with a **Web Api** backend and a **React + TypeScript** frontend.

---

## Project Structure

```
LangChain/
├── langchain-miroservice/   # Python Web API backend
└── langchain-frontend/      # React + TypeScript frontend (Vite)
```

---

## Backend - `langchain-miroservice`

### Features
- 💬 **Chat** with memory - `/chat` (streaming via SSE)
- 🔍 **RAG Chat** - upload a document and ask questions about it
- 🛠️ **Tools** - web search, calculator, datetime, file reader

### Setup

```bash
cd langchain-miroservice

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate        # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env              # macOS/Linux
# copy .env.example .env          # Windows
```

### Environment Variables (`.env`)

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `MODEL_NAME` | Model name (e.g. `gpt-4o-mini`) |
| `SUMMARIZER_MODEL_NAME` | Model used to summarize old conversation history (e.g. `gpt-4o-mini` or for cheaper `gpt-3.5-turbo`) |
| `SUMMARY_TOKEN_THRESHOLD` | Token count before old messages get summarized |

### Run

```bash
python -m uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

---

## Frontend - `langchain-frontend`

### Features
- 💬 **Chat page** - real-time streaming chat with tool badges
- 📄 **RAG page** - drag & drop file upload + document Q&A

### Setup

```bash
cd langchain-frontend
npm install
```

### Run

```bash
npm run dev
```

App available at: `http://localhost:5173`

---

## Quick Start (both together)

Open two terminals:

```bash
# Terminal 1 — Backend
cd langchain-miroservice
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# Terminal 2 — Frontend
cd langchain-frontend
npm run dev
```
