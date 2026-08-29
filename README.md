# jd-gap-agent

A LangGraph-based agent that analyzes a job description, extracts required skills using structured LLM output, and compares them against a candidate's skill set to produce a gap analysis.

Built as a hands-on exercise in agentic AI engineering — async FastAPI, LangGraph orchestration, structured output, and Postgres persistence, containerized and tested with CI.

## What it does

`POST /analyze` takes a raw job description and returns:

- The required skills extracted from the posting (via Claude, using structured/typed output — not regex parsing of free text)
- Which of those skills match a known skill set
- Which are missing

If the input doesn't contain extractable requirements, the agent routes to an error path and returns a clear `422` instead of a silent failure.

## Tech stack

- **FastAPI** (async) — HTTP layer
- **LangGraph** — agent orchestration: structured extraction → conditional routing → tool-based gap analysis
- **LangChain / Anthropic (Claude)** — structured output via `.with_structured_output()`
- **PostgreSQL** (async, via SQLAlchemy + asyncpg) — persistence
- **Docker / Docker Compose** — containerized app + database
- **pytest** — async test suite with mocked LLM calls
- **GitHub Actions** — CI, running tests against a fresh Postgres service on every push



## Architecture

```
Request → FastAPI (/analyze)
            │
            ▼
      LangGraph agent
            │
      ┌─────┴─────┐
      │  extract   │ ← Claude, structured output (ExtractedRequirements)
      └─────┬─────┘
            │
      conditional edge
      (empty skills? → error : match)
            │
      ┌─────┴─────┐
      │   match    │ ← gap analysis tool (set comparison)
      └─────┬─────┘
            │
            ▼
      Postgres (persisted) → JSON response
```


## Running locally

**Requirements:** Docker, Docker Compose, an Anthropic API key.

1. Clone the repo and add your API key:

```bash

   cp .env.example .env

   # edit .env, set ANTHROPIC_API_KEY

```

2. Start everything:

```bash

   docker compose up --build

```

3. Hit the endpoint:

```bash

   curl -X POST [http://127.0.0.1:8000/analyze](http://127.0.0.1:8000/analyze) \

     -H "Content-Type: application/json" \

     -d '{"job_description": "We need a backend engineer with Python, FastAPI, PostgreSQL, and Docker experience."}'

```

   Response:

```json

   {

     "id": 1,

     "job_description": "...",

     "matched_skills": ["python", "fastapi", "postgresql", "docker"],

     "missing_skills": []

   }

```

## Running tests

```bash

pytest tests/ -v

```

Tests mock the LLM call (no API cost, deterministic) but run against a real Postgres instance — locally via Docker, or in CI via a GitHub Actions service container. This validates the actual persistence and routing logic, not just the LLM integration.

## CI/CD

Every push runs the test suite against a clean Postgres instance via GitHub Actions (`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## Project structure

```
app/
├── main.py      # FastAPI app and routes
├── db.py        # Async SQLAlchemy engine/session setup
├── models.py    # Database models (Analysis table)
├── schemas.py   # Pydantic schemas — API I/O and LLM structured output
├── graph.py     # LangGraph agent: nodes, conditional edges, compiled graph
└── tools.py     # Agent tools (gap analysis)
tests/
└── test_analyze.py
docker-compose.yml
Dockerfile
```