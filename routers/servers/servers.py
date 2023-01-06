from _socket import gaierror

from fastapi import APIRouter, Depends, Security, HTTPException, Form
from steam import game_servers as gs
from database import get_session
from jwt_securities import access_security, JAC
from routers.servers.pydantic_models import CreateServer, CreateServerResponse, GetServers
from routers.servers.responses import Responses
from routers.servers.service import get_servers_list, create_server, delete_server_db, get_server_by_uuid
from sqlalchemy.ext.asyncio import AsyncSession as Session

from routers.servers.utils import customClient

router = APIRouter()


@router.get("/servers/", response_model=GetServers)
async def get_servers(db: Session = Depends(get_session),
                      credentials: JAC = Security(access_security)):
    servers = (await get_servers_list(db, credentials["id"])).scalars().all()
    servers = [server.get_security_fields() | await server.get_online() for server in servers]

    return {"response": servers}


@router.delete("/servers/{uuid}")
async def delete_server(uuid: str,
                        db: Session = Depends(get_session),
                        credentials: JAC = Security(access_security)):
    await delete_server_db(db, credentials["id"], uuid)
    await db.commit()
    return {"response": Responses.DEFAULT_OK}


@router.post("/servers/", response_model=CreateServerResponse)
async def create_servers(server: CreateServer = Depends(CreateServer.as_form),
                         db: Session = Depends(get_session),
                         credentials: JAC = Security(access_security)):
    server["owner_id"] = credentials["id"]
    try:
        gs.a2s_info((server["ip_address"], int(server["query_port"])))
    except (TimeoutError, ConnectionRefusedError, gaierror):
        raise HTTPException(status_code=400, detail="Server not found or steam services not answer.")

    new_server = await create_server(db, server)
    await db.commit()
    await db.refresh(new_server)
    return {"response": new_server.get_fields()}


@router.get("/servers/{uuid}/players/")
async def get_players(uuid: str,
                      db: Session = Depends(get_session),
                      credentials: JAC = Security(access_security)):
    server = await get_server_by_uuid(db, uuid, credentials["id"])
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
                        "avatar": "https://avatars.akamai.steamstatic.com/206c3cfc3653a7c2e8ccfae9551873efa6abd9c2_full.jpg",
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
                   db: Session = Depends(get_session),
                   credentials: JAC = Security(access_security)):
    server = await get_server_by_uuid(db, uuid, credentials["id"])

    if not text:
        raise HTTPException(status_code=400, detail='Text is null')

    with customClient(server.ip_address, int(server.rcon_port), passwd=server.rcon_password) as cl:
        cl.run('say', '-1', text)

    return {"response": "ok", "text": text}
