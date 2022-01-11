import json
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from . import models, schemas
from ..settings import settings
from ..ws.connection_manager import manager


logger = logging.getLogger(__name__)


"""
Helpers
"""


def _update_object(obj, update: dict, excluded_keys: List = None):
    for k, v in update.items():
        if k in excluded_keys:
            continue
        setattr(obj, k, v)
    return obj


"""
User CRUD
"""


def get_user(db: Session, _id: Union[str, UUID]) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == _id).first()


def create_user(db: Session, user: schemas.UserCreate, commit: bool = True) -> models.User:
    user = models.User(id=str(uuid4()), **user.dict())
    db.add(user)
    if commit:
        db.commit()
    return user


def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


"""
GameSession CRUD
"""


def get_game_session(db: Session, _id: Union[str, UUID]) -> Optional[models.GameSession]:
    return db.query(models.GameSession).filter(models.GameSession.id == _id).first()


def get_game_sessions(db: Session) -> List[models.GameSession]:
    return db.query(models.GameSession).all()


def get_user_game_sessions(db: Session, user_id: Union[str, UUID]) -> List[models.GameSession]:
    return get_user(db, user_id).game_sessions


def create_game_session(db: Session, session: schemas.GameSessionCreate, commit: bool = True) -> models.GameSession:
    game_session = models.GameSession(id=str(uuid4()), **session.dict())
    db.add(game_session)
    if commit:
        db.commit()
    return game_session


def create_user_game_session(
        db: Session, user: Union[str, UUID, models.User], session: schemas.GameSessionCreate, commit: bool = True
) -> Optional[models.GameSession]:
    if not isinstance(user, models.User):
        user = get_user(db, user)
    if not user:
        return
    try:
        uuid = UUID(session.name, version=4)
        game_session = get_game_session(db, uuid)
    except ValueError:
        game_session = None

    if not game_session:
        game_session = create_game_session(db, session, False)
    elif game_session in user.game_sessions:
        return game_session

    user.game_sessions.append(game_session)
    if commit:
        db.commit()
    return game_session


def delete_user_game_session(
        db: Session, user: Union[str, UUID, models.User], game_session_id: Union[str, UUID], commit: bool = True
) -> bool:
    game_session = get_game_session(db, game_session_id)
    if not game_session:
        return False
    if not isinstance(user, models.User):
        user = get_user(db, user)
    if not user:
        return False
    user.game_sessions.remove(game_session)
    game_session.users.remove(user)
    if not len(game_session.users):
        db.delete(game_session)
    if commit:
        db.commit()
    return True


"""
Marker CRUD
"""


def get_marker(db: Session, _id: Union[str, UUID]) -> Optional[models.Marker]:
    return db.query(models.Marker).filter(models.Marker.id == _id).first()


async def create_marker(db: Session, marker: schemas.MarkerCreate, commit: bool = True) -> models.Marker:
    marker = models.Marker(**marker.dict())
    db.add(marker)
    if commit:
        db.commit()
    await manager.broadcast(marker.game_session_id, json.dumps({
        'id': marker.id,
        'action': 'add'
    }))
    return marker


def get_markers(db: Session, game_session_id: Union[str, UUID]) -> List[models.Marker]:
    return db.query(models.Marker).filter(models.Marker.game_session_id == game_session_id).all()


async def delete_marker(db: Session, marker: Union[str, UUID, models.Marker], commit: bool = True):
    if not isinstance(marker, models.Marker):
        marker = get_marker(db, marker)
    db.delete(marker)
    if commit:
        db.commit()
    await manager.broadcast(marker.game_session_id, json.dumps({
        'id': marker.id,
        'action': 'remove'
    }))
