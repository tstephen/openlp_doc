"""
Connection manager for WebSocket connections
"""

from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for clients"""

    def __init__(self):
        # Dictionary to store active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Set to track all connected client IDs
        self.connected_clients: Set[str] = set()

    async def connect(self, client_id: str, websocket: WebSocket):
        """Accept a WebSocket connection and store it"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connected_clients.add(client_id)
        print(
            f"Client {client_id} connected. Total clients: {len(self.connected_clients)}"
        )

    def disconnect(self, client_id: str):
        """Remove a client connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connected_clients:
            self.connected_clients.remove(client_id)
        print(
            f"Client {client_id} disconnected. Total clients: {len(self.connected_clients)}"
        )

    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(message)

    async def broadcast_slide_update(self, slide_id: str):
        """Broadcast slide update to all connected clients"""
        message = f"slide_update:{slide_id}"
        disconnected_clients = []

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
                print(f"Sent slide update to client {client_id}: {slide_id}")
            except Exception as e:
                print(f"Failed to send message to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    def get_connected_clients(self) -> Set[str]:
        """Get the set of currently connected client IDs"""
        return self.connected_clients.copy()
