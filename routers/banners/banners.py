from fastapi import APIRouter, Depends, Security

from jwt_securities import access_security
from routers.banners.pydantic_models import GetBanners, Banner, CreateBanner
from routers.banners.service import Service

router = APIRouter()


@router.get("/banners/", response_model=GetBanners, responses={422: {"model": None}},
            dependencies=[Security(access_security)])
async def get_banners(offset: int = 0, limit: int = 5, service: Service = Depends(Service)):
    banners_list = await service.get_all_banners()
    return {"response": [banner.get_fields() for banner in banners_list[offset:limit]]}


@router.post("/banners/", response_model=Banner, dependencies=[Security(access_security)])
async def create_banner(banner: CreateBanner = Depends(CreateBanner.as_form), service: Service = Depends(Service)):
    new_banner = await service.add_banner(banner)
    return new_banner.get_fields()
