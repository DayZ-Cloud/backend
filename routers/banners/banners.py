import os

from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession as Session

from database import get_session
from jwt_controller import access_security
from routers.banners import service
from routers.banners.pydantic_models import GetBanners, GetBanner, CreateBanner

router = APIRouter()


@router.get("/banners/", response_model=GetBanners, responses={422: {"model": None}})
async def get_banners(offset: int = 0, limit: int = 5, session: Session = Depends(get_session), credentials: JwtAuthorizationCredentials = Security(access_security)):
    banners_list = await service.get_all_banners(session)
    return {"response": [banner.get_fields() for banner in banners_list[offset:limit]]}


@router.post("/banners/", response_model=GetBanner)
async def create_banner(banner: CreateBanner = Depends(CreateBanner.as_form), session: Session = Depends(get_session), credentials: JwtAuthorizationCredentials = Security(access_security)):
    new_banner = await service.add_banner(session, banner)
    await session.commit()
    await session.refresh(new_banner)
    return {"response": new_banner.get_fields()}
