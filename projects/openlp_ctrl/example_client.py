"""
Example client for OpenLP Control API
"""

import asyncio
import json
from typing import Optional

import httpx
import websockets


class OpenLPControlClient:
    """Simple client for connecting to OpenLP Control server"""

    def __init__(self, server_url: str = "http://127.0.0.1:8000"):
        self.server_url = server_url
        self.websocket_url = server_url.replace("http://", "ws://")
        self.client_id: Optional[str] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None

    async def connect(self, client_id: str):
        """Connect to the server with a client ID"""
        self.client_id = client_id
        websocket_url = f"{self.websocket_url}/connect/{client_id}"

        try:
            self.websocket = await websockets.connect(websocket_url)
            print(f"Connected to server as client: {client_id}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    async def listen_for_updates(self):
        """Listen for slide updates from the server"""
        if not self.websocket:
            print("Not connected to server")
            return

        try:
            async for message in self.websocket:
                print(f"Received: {message}")

                if message.startswith("slide_update:"):
                    slide_id = message.split(":", 1)[1]
                    await self.handle_slide_update(slide_id)
                else:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "heartbeat_response":
                            print("Heartbeat acknowledged")
                    except json.JSONDecodeError:
                        print(f"Received non-JSON message: {message}")

        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed")
        except Exception as e:
            print(f"Error listening for updates: {e}")

    async def handle_slide_update(self, slide_id: str):
        """Handle received slide update"""
        print(f"🎯 New slide: {slide_id}")
        # Add your custom slide handling logic here

    async def send_heartbeat(self):
        """Send heartbeat to server"""
        if self.websocket:
            heartbeat = {
                "type": "heartbeat",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await self.websocket.send(json.dumps(heartbeat))

    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
            print("Disconnected from server")


async def example_client():
    """Example of how to use the client"""
    client = OpenLPControlClient()

    # Connect to server
    if await client.connect("example-client-1"):
        # Listen for updates in the background
        listen_task = asyncio.create_task(client.listen_for_updates())

        # Send periodic heartbeats
        try:
            while True:
                await asyncio.sleep(10)
                await client.send_heartbeat()
        except KeyboardInterrupt:
            print("Client stopped by user")
        finally:
            listen_task.cancel()
            await client.disconnect()


async def example_set_slide():
    """Example of how to set a slide via HTTP API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/set-slide", json={"id": "slide-42"}
            )
            if response.status_code == 200:
                print("Slide update sent successfully")
                print(response.json())
            else:
                print(f"Failed to send slide update: {response.status_code}")
        except Exception as e:
            print(f"Error sending slide update: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "set-slide":
        slide_id = sys.argv[2] if len(sys.argv) > 2 else "test-slide"
        print(f"Setting slide to: {slide_id}")

        # Update the slide ID in the API call
        async def set_specific_slide():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8000/set-slide", json={"id": slide_id}
                )
                print(response.json())

        asyncio.run(set_specific_slide())
    else:
        print("Starting example client...")
        asyncio.run(example_client())
