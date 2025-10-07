"""
FastAPI server for OpenLP Control
"""

import json
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .connection_manager import ConnectionManager

app = FastAPI(title="OpenLP Control", version="0.1.0")

# Global connection manager instance
manager = ConnectionManager()


class SlideUpdate(BaseModel):
    """Model for slide update requests"""

    id: str


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "OpenLP Control Server",
        "version": "0.1.0",
        "connected_clients": len(manager.get_connected_clients()),
    }


@app.websocket("/connect/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for client connections"""
    await manager.connect(client_id, websocket)
    try:
        while True:
            # Keep the connection alive and listen for messages
            data = await websocket.receive_text()

            # Optional: Handle incoming messages from clients
            try:
                message = json.loads(data)
                if message.get("type") == "heartbeat":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "heartbeat_response",
                                "timestamp": message.get("timestamp"),
                            }
                        )
                    )
            except json.JSONDecodeError:
                # Handle non-JSON messages if needed
                pass

    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.post("/set-slide")
async def set_slide(slide_data: SlideUpdate):
    """Set the current slide and broadcast to all connected clients"""
    try:
        await manager.broadcast_slide_update(slide_data.id)
        return {
            "message": f"Slide update sent to all clients",
            "slide_id": slide_data.id,
            "clients_notified": len(manager.get_connected_clients()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to broadcast slide update: {str(e)}"
        )


@app.get("/status")
async def get_status():
    """Get server status and connected clients"""
    return {
        "connected_clients": list(manager.get_connected_clients()),
        "total_connections": len(manager.get_connected_clients()),
    }
