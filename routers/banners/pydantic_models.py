from datetime import datetime

from pydantic import BaseModel

from depends import as_form


@as_form
class CreateBanner(BaseModel):
    index: int
    title: str
    description: str
    background_image: str | None
    link: str | None


class GetBanner(BaseModel):
    response = {
        "id": 1,
        "index": 22,
        "title": "название",
        "description": "описание",
        "background_image": "https://imgs.com/image.png",
        "link": "https://vk.com/anim",
        "created": datetime.now()
    }


class GetBanners(BaseModel):
    response = [GetBanner().response]
