import os

import aiohttp
import requests
from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, ForeignKey

from database import base, CustomBase


class Servers(base, CustomBase):
    __tablename__ = 'servers'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    server_name = Column(String)
    ip_address = Column(String)
    game_port = Column(String)
    rcon_port = Column(String)
    query_port = Column(String)
    rcon_password = Column(String)  # NEED encryption!
    owner_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    WHITELIST = ["id", "server_name"]

    async def get_online(self):
        token = os.getenv("STEAM_API")
        query = {"key": token, "filter": f"addr\\{self.ip_address}:{self.game_port}"}
        async with aiohttp.ClientSession() as session:
            url = f"https://api.steampowered.com/IGameServersService/GetServerLigest/v1/"
            async with session.get(url, params=query) as resp:
                server = await resp.json()

        if not server["response"]:
            return {"max_players": 0, "players": 0}

        server_info = server["response"]["servers"][0]
        return {"max_players": server_info["max_players"], "players": server_info["players"]}
