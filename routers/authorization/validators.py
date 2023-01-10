import re

from fastapi import HTTPException

from routers.authorization.responses import Responses
from routers.authorization.service import Service


async def password_validate(password: str):
    if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
        raise HTTPException(status_code=400, detail=Responses.NOT_VALID_CYRILLIC_OR_LENGTH)


async def registration_validate(user: dict, service: Service):
    is_user_exists = await service.check_user_exists(user["email"])

    if is_user_exists:
        raise HTTPException(status_code=400, detail=Responses.EMAIL_EXISTS)

    if not re.match(r"^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$", user["email"]):
        raise HTTPException(status_code=400, detail=Responses.NOT_VALID_EMAIL)

    await password_validate(user["password"])


async def authorization_validate(user: dict, service: Service):
    instance = await service.password_manager.check_password(user["password"], user["email"])

    if instance is None:
        raise HTTPException(status_code=401, detail=Responses.EMAIL_OR_PASSWORD_NF)

    return instance
