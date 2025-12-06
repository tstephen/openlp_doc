"""
FastAPI server for OpenLP Control
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from .connection_manager import ConnectionManager

app = FastAPI(title="OpenLP Control", version="0.1.0")

# Read CORS origins from environment variable, default to all origins for development
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
# Split by comma if multiple origins are provided
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

# Global connection manager instance
manager = ConnectionManager()

# Global server configuration (will be set by main)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

# Initialize Jinja2 environment
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
templates_dir = Path(__file__).parent / "templates"


def set_server_config(host: str, port: int):
    """Set the server configuration for template rendering"""
    global SERVER_HOST, SERVER_PORT
    SERVER_HOST = host
    SERVER_PORT = port


class SlideUpdate(BaseModel):
    """Model for slide update requests"""

    id: str


@app.get("/openlp_ctrl/js/client.js")
async def get_templated_client_js():
    """Serve the templated client.js with injected server configuration"""
    try:
        template = jinja_env.get_template("client.js.j2")
        rendered_js = template.render(host=SERVER_HOST, port=SERVER_PORT)
        return Response(content=rendered_js, media_type="application/javascript")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering template: {str(e)}"
        )


async def serve_static_file(request_path: str):
    """Serve static files with automatic .html extension detection"""
    if not static_dir.exists():
        raise HTTPException(status_code=404, detail="Static dir not found")

    # Remove leading slash and handle empty path (root)
    clean_path = request_path.lstrip("/")
    if not clean_path:
        clean_path = "index"

    # First try the exact path
    file_path = static_dir / clean_path
    if file_path.is_file():
        return FileResponse(str(file_path))

    # If not found, try with .html extension
    html_path = static_dir / f"{clean_path}.html"
    if html_path.is_file():
        return FileResponse(str(html_path))

    # If still not found, return 404
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/info")
async def api_info():
    """API endpoint with basic server info"""
    return {
        "message": "OpenLP Control Server",
        "version": "0.1.0",
        "connected_clients": len(manager.get_connected_clients()),
    }


@app.websocket("/api/connect/{client_id}")
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


@app.post("/api/set-slide")
async def set_slide(slide_data: SlideUpdate):
    """Set the current slide and broadcast to all connected clients"""
    try:
        await manager.broadcast_slide_update(slide_data.id)
        return {
            "message": "Slide update sent to all clients",
            "slide_id": slide_data.id,
            "clients_notified": len(manager.get_connected_clients()),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to broadcast slide update: {str(e)}",
        )


@app.get("/api/status")
async def get_status():
    """Get server status and connected clients"""
    return {
        "connected_clients": list(manager.get_connected_clients()),
        "total_connections": len(manager.get_connected_clients()),
    }


@app.get("/api/static-files")
async def list_static_files():
    """Debug endpoint to list available static files"""
    if not static_dir.exists():
        return {"error": "Static directory not found"}

    files = []
    for file_path in static_dir.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(static_dir)
            files.append(
                {
                    "path": str(relative_path),
                    "url": f"/static/{relative_path}",
                    "size": file_path.stat().st_size,
                }
            )

    return {
        "static_directory": str(static_dir),
        "files": files,
        "total_files": len(files),
    }


# Catch-all routes for static files (must be last)
@app.get("/")
async def root():
    """Serve the root path"""
    return await serve_static_file("")


@app.get("/{path:path}")
async def catch_all(request: Request, path: str):
    """Catch all non-API routes and serve from static directory"""
    # Skip API routes
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    return await serve_static_file(path)
