from sqlalchemy import Column, String, Integer, DateTime, func

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