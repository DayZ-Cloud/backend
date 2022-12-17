from fastapi import APIRouter, Depends, Security

from database import get_session
from jwt_controller import access_security
from routers.servers.pydantic_models import CreateServer, CreateServerResponse, GetServers
from routers.servers.service import get_servers_list, create_server
from fastapi_jwt import JwtAuthorizationCredentials as JAC
from sqlalchemy.ext.asyncio import AsyncSession as Session

router = APIRouter()


@router.get("/servers/", response_model=GetServers)
async def get_servers(session: Session = Depends(get_session), credentials: JAC = Security(access_security)):
    servers = (await get_servers_list(session, credentials["id"])).scalars().all()
    servers = [server.get_security_fields() | server.get_online() for server in servers]

    return {"response": servers}


@router.post("/servers/", response_model=CreateServerResponse)
async def create_servers(server: CreateServer = Depends(CreateServer.as_form), session: Session = Depends(get_session), credentials: JAC = Security(access_security)):
    server = server.__dict__
    server["owner_id"] = credentials["id"]
    new_server = await create_server(session, server)
    await session.commit()
    await session.refresh(new_server)
    return {"response": new_server.get_fields()}