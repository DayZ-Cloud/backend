from pydantic import BaseModel

from depends import as_form


class ResponseCreateServer(BaseModel):
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str
    uuid: str


@as_form
class CreateServer(BaseModel):
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str
    query_port: str


class Server(BaseModel):
    server_name: str
    players: int
    max_players: int
    status: str
    uuid: str


class CreateServerResponse(BaseModel):
    response: ResponseCreateServer


class GetServers(BaseModel):
    response: list[Server]
