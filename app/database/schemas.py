from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, UUID4


class CreationDateMixin:
    created: datetime


class UserBase(BaseModel, CreationDateMixin):
    id: UUID4

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=36)

    class Config:
        orm_mode = True


class UserDB(UserBase, UserCreate):
    pass


class UserWithGameSessions(UserDB):
    game_sessions: List['GameSessionWithMarkers']


class GameSessionBase(BaseModel, CreationDateMixin):
    id: UUID4

    class Config:
        orm_mode = True


class GameSessionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)

    class Config:
        orm_mode = True


class GameSessionDB(GameSessionBase, GameSessionCreate):
    pass


class GameSessionWithMarkers(GameSessionDB):
    markers: List['MarkerDB']


class MarkerBase(BaseModel, CreationDateMixin):
    id: int
    game_session_id: UUID4

    class Config:
        orm_mode = True


class MarkerCreate(MarkerBase):
    pass


class MarkerDB(MarkerBase):
    pass


UserWithGameSessions.update_forward_refs()
GameSessionWithMarkers.update_forward_refs()
