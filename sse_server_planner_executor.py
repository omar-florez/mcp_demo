# Multi-agent SSE MCP example with Planner and Executor roles + Shared State
# Run with: uvicorn this_file:app --host 0.0.0.0 --port 8000

import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import time
import nest_asyncio
from typing import Optional

nest_asyncio.apply()
app = FastAPI()

# --- Shared Context Object ---

class SharedState:
    def __init__(self, task: str):
        self.task_id = hash(task)
        self.original_task = task
        self.parsed_plan: Optional[str] = None
        self.tool_result: Optional[str] = None

# --- Agent Definitions ---

class PlannerAgent:
    def __init__(self, name="planner"):
        self.name = name

    async def process(self, state: SharedState) -> str:
        await asyncio.sleep(1)
        return f"[{self.name}] Task received: {state.original_task}"

    async def plan(self, state: SharedState) -> str:
        await asyncio.sleep(1)
        state.parsed_plan = f"Compute the result of {state.original_task}"
        return f"[{self.name}] Plan created: {state.parsed_plan}"

class ExecutorAgent:
    def __init__(self, name="executor"):
        self.name = name

    def use_tool(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def execute(self, state: SharedState) -> list[str]:
        await asyncio.sleep(1)
        messages = [
            f"[{self.name}] Received plan: {state.parsed_plan}",
            f"[{self.name}] Invoking tool..."
        ]
        tool_output = self.use_tool(state.original_task)
        state.tool_result = tool_output
        messages.append(f"[{self.name}] {tool_output}")
        return messages

# --- FastAPI SSE Endpoint ---

@app.get("/sse")
async def sse(request: Request, task: str = "2+2"):
    planner = PlannerAgent()
    executor = ExecutorAgent()
    shared_state = SharedState(task=task)

    async def event_stream():
        yield {"data": await planner.process(shared_state)}
        yield {"data": await planner.plan(shared_state)}

        for message in await executor.execute(shared_state):
            yield {"data": message}

        yield {"data": f"[system] Shared tool result: {shared_state.tool_result}"}
        yield {"data": "[system] All agents finished."}

    return EventSourceResponse(event_stream())

# --- Server Entry Point ---

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

start_server()
