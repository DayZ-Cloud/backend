from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count
from database import get_session
from routers.authorization.models import Clients
from routers.servers.models import Servers


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_users_count(self):
        query = await self.session.execute(select(count(Clients.id)))
        return query.scalar()

    async def get_servers_count(self):
        query = await self.session.execute(select(count(Servers.uuid)))
        return query.scalar()