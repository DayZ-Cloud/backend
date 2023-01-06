from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from database import get_session
from routers.banners.models import Banners


class Service:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get_all_banners(self) -> list[Banners]:
        result = await self.session.execute(select(Banners))
        return result.scalars().all()

    async def add_banner(self, banner) -> Banners:
        new_banner = Banners(**banner)
        self.session.add(new_banner)
        await self.session.commit()
        await self.session.refresh(new_banner)
        return new_banner
