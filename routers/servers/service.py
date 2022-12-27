import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from routers.servers.models import Servers


async def get_servers_list(session: AsyncSession, user_id: int):
    return await session.execute(select(Servers).where(Servers.owner_id == user_id))


async def create_server(session: AsyncSession, server: dict):
    if (await session.execute(select(Servers).where(Servers.ip_address == server["ip_address"]))).all():
        raise HTTPException(status_code=400, detail="This IP-Address already exists.")
    server["uuid"] = str(uuid.uuid4())
    server = Servers(**server)
    session.add(server)
    return server


async def get_server_by_uuid(session: AsyncSession, server_uuid: str, user_id: int):
    row = await session.execute(select(Servers).where(Servers.uuid == server_uuid, Servers.owner_id == user_id))
    instance = row.scalar_one()
    return instance


async def delete_server_db(session: AsyncSession, user_id: int, server_uuid: str):
    row = await session.execute(select(Servers).where(Servers.uuid == server_uuid, Servers.owner_id == user_id))
    instance = row.scalar_one()
    if not instance:
        raise HTTPException(status_code=400, detail="This server is not exists, or you does not have access.")

    await session.delete(instance)
