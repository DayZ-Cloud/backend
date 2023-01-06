import re

from fastapi import HTTPException

from routers.authorization.service import Service


async def registration_validate(user: dict, service: Service):
    is_user_exists = await service.check_user_exists(user["email"])

    if is_user_exists:
        raise HTTPException(status_code=400, detail="This email already exists")

    if not re.match(r"^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$", user["email"]):
        raise HTTPException(status_code=400, detail="Not a valid email address")

    if len(user["password"]) < 7 or len(user["password"]) > 32:
        raise HTTPException(status_code=400, detail="Password length must be between 7 or 32")


async def authorization_validate(user: dict, service: Service):
    instance = await service.password_manager.check_password(user["password"], user["email"])
    if instance is None:
        raise HTTPException(status_code=401, detail="This email or password not found.")

    return instance