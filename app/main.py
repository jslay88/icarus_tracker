import os.path
import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .api_v1 import api as api_v1
from .settings import settings
from .ws.routes import router as ws_router


logger = logging.getLogger(__name__)
logger.propagate = True

logger.setLevel(settings.LOG_LEVEL.upper())
logger.addHandler(logging.StreamHandler())

# w
def app():
    logger.info('Creating FastAPI Application for Icarus Tracker...')
    _app = FastAPI()

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )

    logger.info('Mounting APIs...')
    _app.mount('/api/v1', api_v1)

    logger.info('Mounting WebSocket Router...')
    _app.mount('/ws', ws_router)

    logger.info('Mounting Health Check Endpoint...')
    @_app.get('/health')
    def health(): return {'health': 'healthy'}

    if os.path.isdir('static') and os.listdir('static'):
        from fastapi.staticfiles import StaticFiles
        logger.info('Mounting Static...')
        _app.mount('/static', StaticFiles(directory='static', html=True), name='static')

    logger.info('Application Created Successfully.')
    return _app
