import logging

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from .connection_manager import manager
from ..settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL.upper())
logger.propagate = True
router = APIRouter()


logger.info('WebSocket Router Initialized.')


@router.websocket('/{game_session_id}')
async def connect_to_session(websocket: WebSocket, game_session_id: str):
    logger.critical(f'Received Connection to Session: {game_session_id}')
    await manager.connect(websocket, game_session_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f'Data: {data}')
            logger.critical(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_session_id)
