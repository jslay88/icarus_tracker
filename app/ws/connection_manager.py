from typing import List, Optional, Union
from uuid import UUID

from fastapi.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, game_session_id: str):
        await websocket.accept()
        if game_session_id in self.active_connections:
            self.active_connections[game_session_id].append(websocket)
        else:
            self.active_connections[game_session_id] = [websocket]

    def disconnect(self, websocket: WebSocket, game_session_id: str):
        self.active_connections[game_session_id].remove(websocket)

    async def broadcast(self, game_session_id: Optional[Union[str, UUID]], message: str):
        for connection in self.active_connections[str(game_session_id)]:
            await connection.send_text(message)


manager = ConnectionManager()
