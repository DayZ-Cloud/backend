from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials as JAC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from database import get_session
from jwt_controller import access_security
from routers.authorization.models import Clients
from routers.servers.models import Servers
from routers.stats.pydantic_models import GetStat

router = APIRouter()


@router.get("/count/users/", response_model=GetStat)
async def get_users_count(session: Session = Depends(get_session), credentials: JAC = Security(access_security)):
    count_users = len((await session.execute(select(Clients))).scalars().all())
    return {"response": count_users}


@router.get("/count/servers/", response_model=GetStat)
async def get_servers_count(session: Session = Depends(get_session), credentials: JAC = Security(access_security)):
    count_servers = len((await session.execute(select(Servers))).scalars().all())
    return {"response": count_servers}