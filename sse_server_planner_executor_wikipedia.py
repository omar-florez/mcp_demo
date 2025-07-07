# Multi-agent SSE MCP example with Planner and Executor agreement + Real Tool Use (e.g. Wikipedia summary)
# Run with: uvicorn this_file:app --host 0.0.0.0 --port 8000

import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import time
import nest_asyncio
from typing import Optional
import requests

nest_asyncio.apply()
app = FastAPI()

# --- Shared Context Object ---

class SharedState:
    def __init__(self, task: str):
        self.task_id = hash(task)
        self.original_task = task
        self.parsed_plan: Optional[str] = None
        self.executor_approval: Optional[bool] = None
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
        state.parsed_plan = f"Retrieve a summary from Wikipedia about '{state.original_task}'"
        return f"[{self.name}] Plan created: {state.parsed_plan}"

class ExecutorAgent:
    def __init__(self, name="executor"):
        self.name = name

    async def agree_on_plan(self, state: SharedState) -> str:
        await asyncio.sleep(1)
        if "Wikipedia" in state.parsed_plan:
            state.executor_approval = True
            return f"[{self.name}] Approved the plan."
        else:
            state.executor_approval = False
            return f"[{self.name}] Rejected the plan."

    def use_tool(self, topic: str) -> str:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
            response = requests.get(url)
            if response.status_code == 200:
                summary = response.json().get("extract", "No summary found.")
                return summary
            else:
                return f"Wikipedia lookup failed with status {response.status_code}"
        except Exception as e:
            return f"Tool error: {str(e)}"

    async def execute(self, state: SharedState) -> list[str]:
        await asyncio.sleep(1)
        messages = [
            f"[{self.name}] Executing tool with topic: {state.original_task}"
        ]
        tool_output = self.use_tool(state.original_task)
        state.tool_result = tool_output
        messages.append(f"[{self.name}] Tool result: {tool_output[:200]}...")
        return messages

# --- FastAPI SSE Endpoint ---

@app.get("/sse")
async def sse(request: Request, task: str = "Alan_Turing"):
    planner = PlannerAgent()
    executor = ExecutorAgent()
    shared_state = SharedState(task=task)

    async def event_stream():
        yield {"data": await planner.process(shared_state)}
        yield {"data": await planner.plan(shared_state)}

        yield {"data": await executor.agree_on_plan(shared_state)}
        if not shared_state.executor_approval:
            yield {"data": "[system] Executor rejected the plan. Ending session."}
            return

        for message in await executor.execute(shared_state):
            yield {"data": message}

        yield {"data": f"[system] Shared tool result: {shared_state.tool_result[:200]}..."}
        yield {"data": "[system] All agents finished."}

    return EventSourceResponse(event_stream())

# --- Server Entry Point ---

def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

start_server()
