import hashlib
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session

from routers.authorization.models import Clients


async def create_user(session: Session, user):
    user["first_name"] = user["first_name"].capitalize()
    user["last_name"] = user["last_name"].capitalize()
    client = Clients(**user)
    session.add(client)
    return client


async def create_password(password: str) -> hex:
    """
    :param password: пароль для шифровки
    :return: зашифрованный пароль
    """
    return hashlib.sha256(os.getenv("ACCESS_KEY").encode() + password.encode()).hexdigest()


async def check_password(session, password: str, email: str):
    """
    :param session: асинк сессия для БДшки
    :param password: пароль для сравнения (хэшируется и сравнивается с базой данных)
    :param email: логин для сравнения (кому принадлежит пароль)
    :return: подошел ли пароль / логин
    """
    password = await create_password(password)
    return (await session.execute(select(Clients).where(Clients.email == email, Clients.password == password))).first()


async def get_user_by_id(session: Session, user_id: int):
    return await session.execute(select(Clients).where(Clients.id == user_id))


async def get_user_by_email(session: Session, email: str):
    return await session.execute(select(Clients).where(Clients.email == email))