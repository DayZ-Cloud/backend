from sqlalchemy import Column, Integer, String, Text, DateTime, func

from database import base


class News(base):
    __tablename__ = 'news'
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    index = Column(Integer)
    title = Column(String)
    description = Column(Text)
    preview_img = Column(String)
    link = Column(String)
    created = Column(DateTime(timezone=True), server_default=func.now())

    def get_fields(self):
        return {"id": self.id, "index": self.index, "title": self.title, "description": self.description,
                "preview_img": self.preview_img, "link": self.link, "created": self.created}
