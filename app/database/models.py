from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, \
    VARCHAR, UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from . import Base


game_session_associations = Table('game_session_associations',
                                  Base.metadata,
                                  Column('user_id', UUID(as_uuid=True),
                                         ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
                                  Column('game_session_id', UUID(as_uuid=True),
                                         ForeignKey('game_session.id', ondelete='CASCADE'), primary_key=True)
                                  )


"""
Mixins
"""


class CreationDateMixIn(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    created = Column(DateTime, server_default=func.now(), nullable=False)


"""
User Model
"""


class User(Base, CreationDateMixIn):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    username = Column(VARCHAR(36), nullable=False)

    game_sessions = relationship('GameSession', secondary=game_session_associations,
                                 lazy='subquery', cascade='all, delete', passive_deletes=True)


"""
Session Model
"""


class GameSession(Base, CreationDateMixIn):
    __tablename__ = 'game_session'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    name = Column(VARCHAR(64), nullable=False)
    markers = relationship('Marker', uselist=True, cascade='all, delete', passive_deletes=True)

    users = relationship(User, secondary=game_session_associations,
                         lazy='subquery', back_populates='game_sessions')



"""
Marker
"""


class Marker(Base, CreationDateMixIn):
    __tablename__ = 'marker'

    id = Column(Integer, primary_key=True, nullable=False)
    game_session_id = Column(UUID(as_uuid=True), ForeignKey('game_session.id', ondelete='CASCADE'),
                             primary_key=True, nullable=False)
