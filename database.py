from os import getenv
from types import NoneType
from typing import Any

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

engine = create_async_engine(
    f"postgresql+asyncpg://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}",
    echo=False
)
async_session = sessionmaker(bind=engine, class_=AsyncSession)
base = declarative_base()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)
        await conn.run_sync(base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session(expire_on_commit=False) as session:
        yield session


class CustomBase:
    BLACKLIST = []
    WHITELIST = []

    def get_fields(self):
        """
        Вывод всех параметров
        :return:
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def filter(self, value: Any):
        if isinstance(value, (int, NoneType)):
            return value

        return str(value)

    def get_security_fields(self):
        """
        Вывод элементов из черного или белого списка, в зависимости от того, какой пустой
        :return: словарь с элементами
        """
        if self.BLACKLIST:
            return {k: self.filter(v) for k, v in self.__dict__.items() if
                    not k.startswith("_") and k not in self.BLACKLIST}

        if self.WHITELIST:
            return {k: self.filter(v) for k, v in self.__dict__.items() if
                    not k.startswith("_") and k in self.WHITELIST}

        return self.get_fields()
