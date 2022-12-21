from pydantic import BaseModel

from depends import as_form


class ResponseCreateServer(BaseModel):
    id: int
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str


@as_form
class CreateServer(BaseModel):
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str
    query_port: str


class Server(BaseModel):
    id: int
    server_name: str
    players: int
    max_players: int
    status: str


class CreateServerResponse(BaseModel):
    response: ResponseCreateServer


class GetServers(BaseModel):
    response: list[Server]
