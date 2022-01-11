import logging

from fastapi import FastAPI

from .user import router as user_router
from ..settings import settings


logger = logging.getLogger(__name__)


api = FastAPI(title='Icarus Tracker API',
              description='',
              version='1.0.0',
              docs_url='/')


tags_metadata = [
    {
        'name': 'User',
        'description': 'User Endpoints'
    }
]

# Include Endpoint Routers
api.include_router(user_router, prefix='/user', tags=['User'])


# Version Route
@api.get('/version')
def _get_version():
    return {'version': settings.VERSION}
