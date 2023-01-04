from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from routers.news.models import News


async def get_all_news(session: Session) -> list[News]:
    result = await session.execute(select(News))
    return result.scalars().all()


async def add_news(session: Session, news) -> News:
    new_news = News(**news)
    session.add(new_news)
    return new_news
