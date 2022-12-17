from sqlalchemy import Integer, Column, Text, String, DateTime, func

from database import base, CustomBase


class Banners(base, CustomBase):
    __tablename__ = 'banners'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    index = Column(Integer)
    title = Column(String)
    description = Column(Text)
    background_image = Column(String)
    link = Column(String)
    created = Column(DateTime(timezone=True), server_default=func.now())


