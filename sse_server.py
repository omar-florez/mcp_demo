import uvicorn
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import asyncio
import time
import nest_asyncio

nest_asyncio.apply()
app = FastAPI()

# Simulated tool: basic calculator
def use_tool(task: str) -> str:
    try:
        result = eval(task)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

# SSE endpoint for agent-style tool interaction
@app.get("/sse")
async def sse(request: Request, task: str = "2+2"):
    # Lightweight Alternative to WebSockets
    # stream of agent states
    # incremental updates supported by Server-Sent Events (SSE)
    # One long-lived stream, persistent connection,
    # Unlike HTTP/1.1 where each request/response cycle closes the connection, SSE keeps the connection open
    # This is ideal for Long-running agent tasks, Progress updates, Live tool invocations
    async def event_stream():
        yield {"data": f"Agent received task: {task}"}
        await asyncio.sleep(1)
        yield {"data": "Invoking tool..."}
        await asyncio.sleep(1)
        result = use_tool(task)
        yield {"data": result}
        await asyncio.sleep(0.5)
        yield {"data": "[END]"}
    
    return EventSourceResponse(event_stream())

# Launch the server
def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

start_server()
