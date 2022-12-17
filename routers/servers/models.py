import os

import requests
from sqlalchemy import Column, Integer, String, ForeignKey

from database import base, CustomBase


class Servers(base, CustomBase):
    __tablename__ = 'servers'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    server_name = Column(String)
    ip_address = Column(String)
    game_port = Column(String)
    rcon_port = Column(String)
    rcon_password = Column(String)  # NEED encryption!
    owner_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    WHITELIST = ["id", "server_name"]

    def get_online(self):
        token = os.getenv("STEAM_API")
        query = {"key": token, "filter": f"addr\\{self.ip_address}:{self.game_port}"}
        resp = requests.get(f"https://api.steampowered.com/IGameServersService/GetServerList/v1/", params=query)
        server_info = resp.json()["response"]["servers"][0]
        return {"max_players": server_info["max_players"], "players": server_info["players"]}
