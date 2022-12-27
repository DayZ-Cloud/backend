from datetime import timedelta

from sqlalchemy import Column, String, Integer, DateTime, func, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from database import base, CustomBase


class Clients(base, CustomBase):
    __tablename__ = 'clients'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    avatar = Column(String)
    email = Column(String)
    password = Column(String)
    last_auth = Column(DateTime)
    created = Column(DateTime, server_default=func.now())
    BLACKLIST = ["password"]


class Recent(base, CustomBase):
    __tablename__ = "recent"
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    token = Column(UUID)
    key = Column(String)
    expired_at = Column(DateTime)
    client_id = Column(ForeignKey('clients.id'))
