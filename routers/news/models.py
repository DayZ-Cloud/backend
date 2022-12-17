from sqlalchemy import Column, Integer, String, Text, DateTime, func

from database import base, CustomBase


class News(base, CustomBase):
    __tablename__ = 'news'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    index = Column(Integer)
    title = Column(String)
    description = Column(Text)
    preview_img = Column(String)
    link = Column(String)
    created = Column(DateTime(timezone=True), server_default=func.now())
