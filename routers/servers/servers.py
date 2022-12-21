import os
from _socket import gaierror

import requests
from fastapi import APIRouter, Depends, Security, HTTPException
from steam import game_servers as gs
from database import get_session
from jwt_securities import access_security, JAC
from routers.servers.pydantic_models import CreateServer, CreateServerResponse, GetServers
from routers.servers.service import get_servers_list, create_server
from sqlalchemy.ext.asyncio import AsyncSession as Session

router = APIRouter()


@router.get("/servers/", response_model=GetServers)
async def get_servers(db: Session = Depends(get_session),
                      credentials: JAC = Security(access_security)):
    servers = (await get_servers_list(db, credentials["id"])).scalars().all()
    servers = [server.get_security_fields() | await server.get_online() for server in servers]

    return {"response": servers}


@router.post("/servers/", response_model=CreateServerResponse)
async def create_servers(server: CreateServer = Depends(CreateServer.as_form),
                         db: Session = Depends(get_session),
                         credentials: JAC = Security(access_security)):
    server = server.__dict__
    server["owner_id"] = credentials["id"]
    try:
        gs.a2s_info((server["ip_address"], int(server["query_port"])))
    except gaierror:
        raise HTTPException(status_code=400, detail="Server not found or steam services not answer.")

    new_server = await create_server(db, server)
    await db.commit()
    await db.refresh(new_server)
    return {"response": new_server.get_fields()}