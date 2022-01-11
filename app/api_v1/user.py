from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import crud, get_db, models, schemas
from ..settings import settings


router = APIRouter()


@router.get('/', response_model=List[schemas.UserDB])
def get_users(db: Session = Depends(get_db)) -> List[Union[models.User, schemas.UserDB]]:
    return crud.get_users(db)


@router.get('/{user_id}', response_model=schemas.UserWithGameSessions)
def get_user(user_id: str, db: Session = Depends(get_db)) -> Union[models.User, schemas.UserDB]:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User ID: {user_id}'
        )
    return user


@router.post('/{invite_code}', response_model=schemas.UserDB)
def create_user(
        invite_code: str, user: schemas.UserCreate, db: Session = Depends(get_db)
) -> Union[models.User, schemas.UserDB]:
    if invite_code != settings.INVITE_CODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'We don\'t want to play'
        )
    return crud.create_user(db, user)


@router.get('/{user_id}/game_session')
def get_user_game_sessions(
        user_id: str, db: Session = Depends(get_db)
) -> List[Union[models.GameSession, schemas.GameSessionDB]]:
    return crud.get_user_game_sessions(db, user_id)


@router.get('/{user_id}/game_session/{game_session_id}', response_model=schemas.GameSessionWithMarkers)
def get_game_session(
        user_id: str, game_session_id: str, db: Session = Depends(get_db)
) -> List[Union[models.GameSession, schemas.GameSessionDB]]:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    for game_session in user.game_sessions:
        if str(game_session.id) == game_session_id:
            return game_session
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Game Session ID: {game_session_id}'
    )


@router.post('/{user_id}/game_session', response_model=schemas.GameSessionWithMarkers)
def create_user_game_session(
        user_id: str, game_session: schemas.GameSessionCreate, db: Session = Depends(get_db)
) -> Union[models.GameSession, schemas.GameSessionDB]:
    return crud.create_user_game_session(db, user_id, game_session)


@router.delete('/{user_id}/game_session/{game_session_id}')
def delete_user_game_session(
        user_id: str, game_session_id: str, db: Session = Depends(get_db)
):
    if crud.delete_user_game_session(db, user_id, game_session_id):
        return ''
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Game Session ID: {game_session_id}'
    )


@router.post('/{user_id}/game_session/{game_session_id}/marker/{marker_id}', response_model=schemas.MarkerDB)
async def add_marker(
        user_id: str, game_session_id: str, marker_id: str, db: Session = Depends(get_db)
) -> Union[models.Marker, schemas.MarkerDB]:
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    for game_session in user.game_sessions:
        if str(game_session.id) == game_session_id:
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Game Session not found: {game_session_id}'
        )
    return await crud.create_marker(db, schemas.MarkerCreate(id=marker_id, game_session_id=game_session_id))


@router.delete('/{user_id}/game_session/{game_session_id}/marker/{marker_id}')
async def delete_marker(user_id: str, game_session_id: str, marker_id: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    for game_session in user.game_sessions:
        if str(game_session.id) == game_session_id:
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Game Session not found: {game_session_id}'
        )
    await crud.delete_marker(db, marker_id)
    return
