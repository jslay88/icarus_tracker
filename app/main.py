import os.path
import logging

from fastapi import FastAPI, HTTPException, Response, status
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
        if os.path.isfile('static/userscript/script.js'):
            logger.info('Userscript detected, creating update.js route...')
            with open('static/userscript/script.js') as f:
                for line in f.readlines():
                    if line.startswith('// @version'):
                        version = line.strip()
                        break
                else:
                    version = '// @version      100.0'

            @_app.get('/static/userscript/update.js')
            def script_update():
                data = f'// ==UserScript==\n{version}\n// ==/UserScript==\n'
                return Response(content=data, media_type='application/javascript')

        from fastapi.staticfiles import StaticFiles
        logger.info('Mounting Static...')
        _app.mount('/static', StaticFiles(directory='static', html=True), name='static')

    logger.info('Application Created Successfully.')
    return _app
