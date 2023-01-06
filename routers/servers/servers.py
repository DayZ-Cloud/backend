from fastapi import APIRouter, Depends, Security, HTTPException, Form
from jwt_securities import access_security, JAC
from routers.servers.pydantic_models import CreateServer, GetServers, ResponseCreateServer
from routers.servers.responses import Responses
from routers.servers.service import Service

from routers.servers.utils import customClient
from routers.servers.validators import check_server_exists

router = APIRouter()


@router.get("/servers/", response_model=GetServers)
async def get_servers(service: Service = Depends(Service), credentials: JAC = Security(access_security)):
    servers = await service.get_servers_list(credentials["id"])
    servers = [server.get_security_fields() | await server.get_online() for server in servers]

    return {"response": servers}


@router.delete("/servers/{uuid}")
async def delete_server(uuid: str,
                        service: Service = Depends(Service),
                        credentials: JAC = Security(access_security)):
    await service.delete_server_db(credentials["id"], uuid)
    return {"response": Responses.DEFAULT_OK}


@router.post("/servers/", response_model=ResponseCreateServer)
async def create_servers(server: dict = Depends(CreateServer.as_form),
                         service: Service = Depends(Service),
                         credentials: JAC = Security(access_security)):
    server["owner_id"] = credentials["id"]
    await check_server_exists(server["ip_address"], int(server["query_port"]))

    new_server = await service.create_server(server)
    return new_server.get_fields()


@router.get("/servers/{uuid}/players/")
async def get_players(uuid: str,
                      service: Service = Depends(Service),
                      credentials: JAC = Security(access_security)):
    # дserver = await service.get_server_by_uuid(uuid, credentials["id"])
    return {"response": {
        "sessions": [
            {
                "connection": {
                    "country_code": "RU",
                    "ipv4": "217.199.209.159",
                    "provider": "Rostelecom"
                },
                "gamedata": {
                    "player_name": "Mixxe73",
                    "steam64": "76561199088333827"
                },
                "persona": {
                    "bans": {
                        "vac": 0
                    },
                    "profile": {
                        "avatar": "https://avatars.akamai.steamstatic.com"
                                  "/206c3cfc3653a7c2e8ccfae9551873efa6abd9c2_full.jpg",
                        "name": "boriz",
                        "private": False
                    }
                },
                "live": {
                    "ping": {
                        "actual": 62,
                    },
                },
            },
        ],
        "status": True
    }}


@router.post("/servers/{uuid}/send-message/")
async def say_rcon(uuid: str, text: str = Form(...),
                   service: Service = Depends(Service),
                   credentials: JAC = Security(access_security)):
    server = await service.get_server_by_uuid(uuid, credentials["id"])

    if not text:
        raise HTTPException(status_code=400, detail='Text is null')

    with customClient(server.ip_address, int(server.rcon_port), passwd=server.rcon_password) as cl:
        cl.run('say', '-1', text)

    return {"response": "ok", "text": text}
