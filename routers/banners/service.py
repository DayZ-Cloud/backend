from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from routers.banners.models import Banners


async def get_all_banners(session: Session) -> list[Banners]:
    result = await session.execute(select(Banners))
    return result.scalars().all()


async def add_banner(session: Session, banner) -> Banners:
    new_banner = Banners(**banner)
    session.add(new_banner)
    return new_banner
