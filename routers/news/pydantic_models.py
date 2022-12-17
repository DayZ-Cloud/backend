from datetime import datetime

from pydantic import BaseModel

from depends import as_form


@as_form
class CreateNews(BaseModel):
    index: int
    title: str
    description: str
    preview_img: str
    link: str | None


class GetOneNews(BaseModel):
    response = {
        "id": 1,
        "index": 22,
        "title": "название",
        "description": "описание",
        "preview_img": "https://imgs.com/image.png",
        "link": "https://vk.com/anim",
        "created": datetime.now()
    }


class GetNews(BaseModel):
    response = [GetOneNews().response]
