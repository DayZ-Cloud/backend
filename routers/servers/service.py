import celery
from fastapi import HTTPException, Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from celery_handler import celery_app
from database import get_session
from routers.servers.models import Servers


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_servers_list(self, user_id: int):
        query = await self.session.execute(select(Servers).where(Servers.owner_id == user_id))
        return query.scalars().all()

    async def create_server(self, server: dict):
        query = exists().where(Servers.ip_address == server["ip_address"], Servers.query_port == server["query_port"]).select()
        query = await self.session.execute(query)

        if query.scalar():
            raise HTTPException(status_code=400, detail="This IP-Address already exists.")

        server = Servers(**server)
        self.session.add(server)
        await self.session.commit()
        await self.session.refresh(server)
        return server

    async def get_server_by_uuid(self, server_uuid: str, user: int):
        query = await self.session.execute(select(Servers).where(Servers.uuid == server_uuid, Servers.owner_id == user))
        return query.scalars().first()

    async def delete_server_db(self, user: str, server_uuid: str):
        query = await self.session.execute(select(Servers).where(Servers.uuid == server_uuid, Servers.owner_id == user))
        instance = query.scalars().first()

        if not instance:
            raise HTTPException(status_code=400, detail="This server is not exists, or you does not have access.")

        await self.session.delete(instance)
        await self.session.commit()
