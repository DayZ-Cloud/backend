from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession as Session

from database import get_session
from jwt_securities import access_security, JAC
from routers.banners import service
from routers.banners.pydantic_models import GetBanners, Banner, CreateBanner

router = APIRouter()


@router.get("/banners/", response_model=GetBanners, responses={422: {"model": None}})
async def get_banners(offset: int = 0, limit: int = 5,
                      db: Session = Depends(get_session),
                      credentials: JAC = Security(access_security)):
    banners_list = await service.get_all_banners(db)
    return {"response": [banner.get_fields() for banner in banners_list[offset:limit]]}


@router.post("/banners/", response_model=Banner)
async def create_banner(banner: CreateBanner = Depends(CreateBanner.as_form),
                        db: Session = Depends(get_session),
                        credentials: JAC = Security(access_security)):
    new_banner = await service.add_banner(db, banner)
    await db.commit()
    await db.refresh(new_banner)
    return {"response": new_banner.get_fields()}
