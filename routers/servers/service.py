from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from routers.servers.models import Servers


async def get_servers_list(session: AsyncSession, user_id: int):
    return await session.execute(select(Servers).where(Servers.owner_id == user_id))


async def create_server(session: AsyncSession, server: dict):
    server = Servers(**server)
    session.add(server)
    return server
