from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database import engine, get_session
from jwt_securities import access_security, JAC
from routers.news import service
from routers.news.pydantic_models import CreateNews, GetNews, GetCreated

router = APIRouter()
session = sessionmaker(bind=engine, class_=AsyncSession)()


@router.get("/news/", response_model=GetNews, responses={422: {"model": None}})
async def get_news(offset: int = 0, limit: int = 5,
                   session: AsyncSession = Depends(get_session),
                   credentials: JAC = Security(access_security)):
    news_list = await service.get_all_news(session)
    return {"response": [news.get_fields() for news in news_list[offset:limit]]}


@router.post("/news/", response_model=GetCreated)
async def create_news(credentials: JAC = Security(access_security),
                      news: CreateNews = Depends(CreateNews.as_form),
                      session: AsyncSession = Depends(get_session)):
    new_news = await service.add_news(session, news)
    await session.commit()
    await session.refresh(new_news)
    return {"response": new_news.get_fields()}
