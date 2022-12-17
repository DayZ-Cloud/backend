from pydantic import BaseModel

from depends import as_form


@as_form
class CreateServer(BaseModel):
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str


class Server(BaseModel):
    id: int
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str
    owner_id: int


class CreateServerResponse(BaseModel):
    response: Server


class GetServers(BaseModel):
    response: list[Server]