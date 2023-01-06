from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database import engine
from jwt_securities import access_security
from routers.news.pydantic_models import CreateNews, GetNews, GetCreated
from routers.news.service import Service

router = APIRouter()
session = sessionmaker(bind=engine, class_=AsyncSession)()


@router.get("/news/", response_model=GetNews, responses={422: {"model": None}},
            dependencies=[Security(access_security)])
async def get_news(offset: int = 0, limit: int = 5, service: Service = Depends(Service)):
    news_list = await service.get_all_news()
    return {"response": [news.get_fields() for news in news_list[offset:limit]]}


@router.post("/news/", response_model=GetCreated, dependencies=[Security(access_security)])
async def create_news(news: CreateNews = Depends(CreateNews.as_form),
                      service: Service = Depends(Service)):
    new_news = await service.add_news(news)
    return new_news.get_fields()
