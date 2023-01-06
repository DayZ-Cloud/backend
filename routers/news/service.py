from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from database import get_session
from routers.news.models import News


class Service:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def get_all_news(self) -> list[News]:
        result = await self.session.execute(select(News))
        return result.scalars().all()

    async def add_news(self, news) -> News:
        new_news = News(**news)
        self.session.add(new_news)
        await self.session.commit()
        await self.session.refresh(new_news)
        return new_news
