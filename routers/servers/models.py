import os

import requests
from sqlalchemy import Column, Integer, String, ForeignKey

from database import base


class Servers(base):
    __tablename__ = 'servers'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    server_name = Column(String)
    ip_address = Column(String)
    game_port = Column(String)
    rcon_port = Column(String)
    rcon_password = Column(String)  # NEED encryption!
    owner_id = Column(Integer,
                      ForeignKey('clients.id', ondelete='CASCADE'),
                      nullable=False)

    def get_security_fields(self):
        return {"id": self.id, "name": self.server_name}

    def get_online(self):
        token = os.getenv("STEAM_API")
        query = {"key": token, "filter": f"addr\\{self.ip_address}:{self.game_port}"}
        resp = requests.get(f"https://api.steampowered.com/IGameServersService/GetServerList/v1/", params=query)
        server_info = resp.json()["response"]["servers"][0]
        return {"max_players": server_info["max_players"], "players": server_info["players"]}

    def get_fields(self):
        return {"id": self.id, "name": self.server_name, "ip_address": self.ip_address, "game_port": self.game_port,
                "rcon_port": self.rcon_port, "rcon_password": self.rcon_password, "owner_id": self.owner_id}
