import os
import json
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from websocket_client import WebSocketClient

API_BASE_URL = os.getenv("API_BASE_URL", "ws://ofa-api:8000")
templates = Jinja2Templates(directory="templates")

ws_client = WebSocketClient(API_BASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    await ws_client.initialize()
    yield
    print("Shutting down...")
    await ws_client.cleanup()

app = FastAPI(
    title="Dashboard", 
    description="Real-time monitoring of lab-usine equipments",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

async def create_sse_stream() -> AsyncGenerator[str, None]:
    """
    Create Server-Sent Events stream.
    """
    last_ping = asyncio.get_event_loop().time()
    ping_interval = 30
    
    while True:
        try:
            try:
                message = await asyncio.wait_for(
                    ws_client.message_queue.get(), 
                    timeout=1.0
                )
                yield f"data: {json.dumps(message)}\n\n"
                
            except asyncio.TimeoutError:
                current_time = asyncio.get_event_loop().time()
                if current_time - last_ping > ping_interval:
                    yield f"data: {json.dumps({'event': 'ping'})}\n\n"
                    last_ping = current_time
            
        except Exception as e:
            print(f"Error in SSE stream: {e}")
            error_msg = {'event': 'error', 'message': str(e)}
            yield f"data: {json.dumps(error_msg)}\n\n"
            await asyncio.sleep(1)

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": list(ws_client.devices.keys()),
            "device": {}
        }
    )

@app.get("/devices/{device_uuid}", response_class=HTMLResponse)
async def device_detail(request: Request, device_uuid: str):
    """Device page"""
    device = ws_client.devices.get(device_uuid)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": list(ws_client.devices.keys()),
            "device_uuid": device_uuid,
            "device_dataitems": device["dataitems"],
            "dataitems_stats": device["stats"],
        }
    )

@app.get("/updates/all")
async def stream_updates():
    """Server-sent events endpoint"""
    return StreamingResponse(
        create_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/simulation-mode/{device_uuid}")
async def set_simulation_mode(device_uuid: str, request: Request):
    """Set device simulation mode"""
    try:
        data = await request.json()
        enabled = data.get("enabled", False)
        
        if device_uuid not in ws_client.devices:
            raise HTTPException(status_code=404, detail="Device not found")
        
        response = await ws_client.send_simulation_mode(device_uuid, enabled)
        return response
        
    except Exception as e:
        print(f"Failed to set simulation mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices")
async def get_all_devices():
    """Get all devices"""
    return {"devices": ws_client.devices}

@app.get("/api/devices/{device_uuid}")
async def get_device(device_uuid: str):
    """Get specific device"""
    device = ws_client.devices.get(device_uuid)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"device": device}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)