import uuid

from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import base, CustomBase


class Clients(base, CustomBase):
    __tablename__ = 'clients'
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    avatar = Column(String)
    email = Column(String)
    password = Column(String)
    last_auth = Column(DateTime)
    created = Column(DateTime, server_default=func.now())
    BLACKLIST = ["password", "id"]


class Recent(base, CustomBase):
    __tablename__ = "recent"
    id = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    token = Column(UUID(as_uuid=True))
    key = Column(String)
    expired_at = Column(DateTime)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'))
    client = relationship("clients", backref="client_id")
