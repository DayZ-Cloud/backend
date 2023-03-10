import datetime
import hashlib
import os
import re

from fastapi import HTTPException, Depends
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession as Session
from starlette.status import HTTP_400_BAD_REQUEST

from database import get_session
from routers.authorization.models import Clients, Recent
from routers.authorization.responses import Responses


class PasswordMethods:
    def __init__(self, session: Session):
        self.session = session
        self.token = os.getenv("ACCESS_KEY").encode()

    async def create_password(self, password: str) -> hex:
        """
        :param password: пароль для шифровки
        :return: зашифрованный пароль
        """
        return hashlib.sha256(self.token + password.encode()).hexdigest()

    async def check_password(self, password: str, email: str):
        """
        :param password: пароль для сравнения (хэшируется и сравнивается с базой данных)
        :param email: логин для сравнения (кому принадлежит пароль)
        :return: Model instance
        """
        password = await self.create_password(password)
        query = await self.session.execute(select(Clients).where(Clients.email == email, Clients.password == password))
        return query.scalars().first()

    async def password_validate(self, password: str):
        if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            raise HTTPException(status_code=400, detail=Responses.NOT_VALID_CYRILLIC_OR_LENGTH)


class Service:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        self.password_manager = PasswordMethods(session)

    async def create_user(self, user):
        user["first_name"] = user["first_name"].capitalize()
        user["last_name"] = user["last_name"].capitalize()
        user["password"] = await self.password_manager.create_password(password=user["password"])
        client = Clients(**user)
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        return client

    async def check_reset(self, old_password: str, new_password: str, user_email: str):
        instance = await self.password_manager.check_password(password=old_password, email=user_email)

        if not instance:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.RESET_PASSWORD_NOT_CORRECT)

        await self.password_manager.password_validate(new_password)

        if old_password == new_password:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.SAME_PASSWORDS)

        instance.password = await self.password_manager.create_password(new_password)
        await self.session.commit()

    async def get_user_by_id(self, user_id: int):
        query = await self.session.execute(select(Clients).where(Clients.id == user_id))
        return query.scalars().first()

    async def get_user_by_email(self, email: str):
        query = await self.session.execute(select(Clients).where(Clients.email == email))
        return query.scalars().first()

    async def set_auth(self, email: str):
        user = await self.get_user_by_email(email)

        user.last_auth = datetime.datetime.now()
        await self.session.commit()

    async def check_user_exists(self, email: str = None, user_id: str = None):
        query = []

        if email is not None:
            query.append(Clients.email == email)

        if user_id is not None:
            query.append(Clients.id == user_id)

        query = await self.session.execute(exists().where(*query).select())
        return query.scalar()

    async def create_recent(self, email: str, token_data):
        instance = await self.get_user_by_email(email)
        if not instance:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.USER_NOT_EXISTS)

        token_data["client_id"] = instance.id
        recent = Recent(**token_data)

        self.session.add(recent)
        await self.session.commit()
        return recent

    async def check_recent(self, uuid: str, key: str, password: str):
        query = await self.session.execute(select(Recent).where(Recent.token == uuid, Recent.key == key))
        token = query.scalars().first()
        if not token:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.RECENT_NOT_FOUND)

        if token.expired_at < datetime.datetime.now():
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.RECENT_EXPIRED)

        user_query = await self.session.execute(select(Clients).where(Clients.id == token.client_id))
        user = user_query.scalars().first()

        await self.password_manager.password_validate(password)

        if not user:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.USER_NOT_EXISTS)

        user.password = await self.password_manager.create_password(password)
        await self.session.delete(token)
        await self.session.commit()
