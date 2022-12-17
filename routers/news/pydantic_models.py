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


class OneNews(BaseModel):
    id: int
    index: int
    title: str
    description: str
    preview_img: str
    link: str
    created: datetime


class GetCreated(BaseModel):
    response: OneNews

    class Config:
        schema_extra = {
            'examples': [
                {"response": {
                    "id": 1,
                    "index": 5,
                    "title": "Экстренное обновление ядра",
                    "description": "Сегодня ночью произойдет обновление ядра системы. Это необходимо для сохранности "
                                   "и безопасности ваших данных.",
                    "preview_img": "https://i.imgur.com/S1OPVB6.jpeg",
                    "link": "http://discord.gg/hvUr2UGHSV",
                    "created": datetime.now()
                }}
            ]
        }


class GetNews(BaseModel):
    response: list[OneNews]

    class Config:
        schema_extra = {
            'examples': [
                {"response": [{
                    "id": 1,
                    "index": 5,
                    "title": "Экстренное обновление ядра",
                    "description": "Сегодня ночью произойдет обновление ядра системы. Это необходимо для сохранности и безопасности ваших данных.",
                    "preview_img": "https://i.imgur.com/S1OPVB6.jpeg",
                    "link": "http://discord.gg/hvUr2UGHSV",
                    "created": datetime.now()
                }]}
            ]
        }