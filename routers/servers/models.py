import os
from _socket import gaierror

import aiohttp
import requests
from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from steam import game_servers as gs
from database import base, CustomBase


class Servers(base, CustomBase):
    __tablename__ = 'servers'
    uuid = Column(UUID, nullable=False, unique=True, primary_key=True)
    server_name = Column(String)
    ip_address = Column(String)
    game_port = Column(String)
    rcon_port = Column(String)
    query_port = Column(String)
    rcon_password = Column(String)  # NEED encryption!
    owner_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    WHITELIST = ["server_name", "uuid"]

    async def get_online(self):
        try:
            server = gs.a2s_info((self.ip_address, int(self.query_port)))
        except gaierror:
            return {"max_players": 0, "players": 0, "status": "offline"}

        return {"max_players": server["max_players"], "players": server["players"], "status": "online"}
