from _socket import gaierror

import uuid as uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from steam import game_servers as gs
from database import base, CustomBase


class Servers(base, CustomBase):
    __tablename__ = 'servers'
    uuid = Column(UUID(as_uuid=True), nullable=False, unique=True, primary_key=True, default=uuid.uuid4)
    server_name = Column(String)
    ip_address = Column(String)
    game_port = Column(String)
    rcon_port = Column(String)
    query_port = Column(String)
    rcon_password = Column(String)  # NEED encryption!
    owner_id = Column(UUID(as_uuid=True), ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    WHITELIST = ["server_name", "uuid"]

    async def get_online(self):
        try:
            server = gs.a2s_info((self.ip_address, int(self.query_port)), timeout=0.5)
            print(server)
        except (gaierror, TimeoutError, ConnectionRefusedError):
            return {"max_players": 0, "players": 0, "status": "offline"}

        return {"max_players": server["max_players"], "players": server["players"], "status": "online"}
