import datetime
import hashlib
import os
import uuid

from fastapi import HTTPException
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession as Session
from starlette.status import HTTP_400_BAD_REQUEST

from routers.authorization.models import Clients, Recent


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


async def check_user_exists(session: Session, email: str = None, user_id: str = None):
    query = []

    if email is not None:
        query.append(Clients.email == email)

    if user_id is not None:
        query.append(Clients.id == user_id)

    return await session.execute(exists().where(*query).select())


async def get_user_by_email(session: Session, email: str):
    return await session.execute(select(Clients).where(Clients.email == email))


async def create_recent(session: Session, email: str, token_data):
    if not (user := (await get_user_by_email(session, email)).all()):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not exists")
    token_data["client_id"] = user[0][0].id
    recent = Recent(**token_data)
    session.add(recent)
    return recent


async def check_recent(session: Session, uuid: str, key: str, password: str):
    token = await session.execute(select(Recent).where(Recent.token == uuid, Recent.key == key))
    if not (token := token.all()):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="This token or key not found.")

    token = token[0][0]
    if token.expired_at < datetime.datetime.now():
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="This token and key expired")

    user = await session.execute(select(Clients).where(Clients.id == token.client_id))
    if not (user := user.all()):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found.")

    user = user[0][0]
    user.password = await create_password(password)
    await session.delete(token)
    await session.commit()


async def check_reset(session: Session, old_password: str, new_password: str, user_email: str):
    if not (instance := await check_password(session, password=old_password, email=user_email)):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Password not correct")
    instance[0].password = await create_password(new_password)
    await session.commit()


async def set_auth(session: Session, email: str):
    user = await get_user_by_email(session, email)

    user.all()[0][0].last_auth = datetime.datetime.now()
    await session.commit()