from fastapi import APIRouter, Depends, Security
from jwt_securities import access_security
from routers.stats.pydantic_models import GetUsersCount, GetServersCount
from routers.stats.services import Service

router = APIRouter()


@router.get("/count/users/", responses={200: {"model": GetUsersCount}}, dependencies=[Security(access_security)])
async def get_users_count(service: Service = Depends(Service)):
    count_users = await service.get_users_count()
    return {"users_count": count_users}


@router.get("/count/servers/", responses={200: {"model": GetServersCount}}, dependencies=[Security(access_security)])
async def get_servers_count(service: Service = Depends(Service)):
    count_servers = await service.get_servers_count()
    return {"servers_count": count_servers}
