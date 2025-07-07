# Model Context Protocol (MCP) Demo

This repository showcases multiple agent coordination using a minimal Model Context Protocol (MCP) architecture, built with FastAPI and Server-Sent Events (SSE). Each example implements structured agent collaboration with shared state, planning, validation, and tool usage.

## Features

- Multi-agent coordination (Planner, Executor, Critic)
- Shared memory through structured context objects
- Server-Sent Events (SSE) for streaming updates
- Real tool integration (e.g., Wikipedia API, math expression evaluation)
- Modular and extensible agent definitions

## Examples

### 1. `sse_server.py`
**Description:**  
Single-agent demo using SSE to evaluate simple math expressions.

**Run:**
```bash
python sse_server.py
```

**Test:**
```bash
curl "http://localhost:8000/sse?task=2*(3+4)"
```

---

### 2. `sse_server_planner_executor.py`
**Description:**  
Two-agent interaction between a `PlannerAgent` and an `ExecutorAgent`. The planner defines a computation plan; the executor evaluates it using Python's `eval()`.

**Run:**
```bash
python sse_server_planner_executor.py
```

**Test:**
```bash
curl "http://localhost:8000/sse?task=3*(5+1)"
```

---

### 3. `sse_server_planner_executor_wikipedia.py`
**Description:**  
Full MCP pipeline with `PlannerAgent`, `ExecutorAgent`, and Wikipedia integration. The planner proposes a summary retrieval task, and the executor runs it via the Wikipedia REST API after validating the plan.

**Run:**
```bash
python sse_server_planner_executor_wikipedia.py
```

**Test:**
```bash
curl "http://localhost:8000/sse?task=Alan_Turing"
```

---

## How It Works

All examples use FastAPI's `EventSourceResponse` to simulate long-running agent workflows. Agents pass a `SharedState` object containing task metadata, plan content, approval flags, and tool results.

## Dependencies

```bash
pip install fastapi sse-starlette uvicorn nest_asyncio requests
```

## License

MIT License