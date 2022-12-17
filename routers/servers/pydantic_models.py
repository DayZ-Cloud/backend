from pydantic import BaseModel

from depends import as_form


@as_form
class CreateServer(BaseModel):
    server_name: str
    ip_address: str
    game_port: str
    rcon_port: str
    rcon_password: str


class CreateServerResponse(BaseModel):
    response = {
        "id": "integer",
        "server_name": "string",
        "ip_address": "string",
        "game_port": "string",
        "rcon_port": "string",
        "rcon_password": "string",
        "owner_id": "integer"
    }


class GetServers(BaseModel):
    response = [
        {
            "id": 2,
            "name": 'string',
            "players": 'integer',
            "max_players": 'integer'
        }
    ]