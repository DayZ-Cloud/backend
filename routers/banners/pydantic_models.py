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


class Banner(BaseModel):
    id: int
    index: int
    title: str
    description: str
    background_image: str | None
    link: str | None
    created: datetime
    

class GetBanners(BaseModel):
    response: list[Banner]
