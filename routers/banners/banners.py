from fastapi import APIRouter, Depends, Security

from jwt_securities import access_security
from routers.banners.pydantic_models import Banner, CreateBanner
from routers.banners.service import Service

router = APIRouter()


@router.get("/banners/", responses={422: {"model": None}, 200: {"model": list[Banner]}},
            dependencies=[Security(access_security)])
async def get_banners(offset: int = 0, limit: int = 5, service: Service = Depends(Service)):
    banners_list = await service.get_all_banners()
    return [banner.get_fields() for banner in banners_list[offset:limit]]


@router.post("/banners/", dependencies=[Security(access_security)], responses={200: {"model": Banner}})
async def create_banner(banner: CreateBanner = Depends(CreateBanner.as_form), service: Service = Depends(Service)):
    new_banner = await service.add_banner(banner)
    return new_banner.get_fields()
