import re

from fastapi import APIRouter, Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials as JAC
from sqlalchemy.ext.asyncio import AsyncSession as Session
from starlette.responses import JSONResponse

from database import get_session
from jwt_controller import access_security, refresh_security
from routers.authorization import service
from routers.authorization.pydantic_models import Registration, Credentials, RegistrationReturn, TokenReturn, \
    RegistrationError
from routers.authorization.service import get_user_by_email, check_password, create_password, get_user_by_id

router = APIRouter()


@router.post("/registration/", responses={200: {"model": RegistrationReturn}, 400: {"model": RegistrationError}})
async def registration(user: Registration = Depends(Registration.as_form), session: Session = Depends(get_session)):
    user = user.__dict__
    user_exists = await get_user_by_email(session, user["email"])

    if user_exists.all():
        return JSONResponse(status_code=400, content={"detail": "This email already exists"})

    if not re.match(r"^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$", user["email"]):
        return JSONResponse(status_code=400, content={"detail": "Not a valid email address"})

    if len(user["password"]) < 7 or len(user["password"]) > 32:
        return JSONResponse(status_code=400, content={"detail": "Password length must be between 7 or 32"})

    user["password"] = await service.create_password(password=user["password"])
    new_user = await service.create_user(session, user)

    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.post("/token/", response_model=TokenReturn)
async def obtain_token(credentials: Credentials = Depends(Credentials.as_form),
                       session: Session = Depends(get_session)):
    user = credentials.__dict__
    if (user_auth := await check_password(session, user["password"], user["email"])) is None:
        return JSONResponse(status_code=401, content={"detail": "This email or password not found."})

    user["password"] = await create_password(user["password"])
    del user["password"]
    user["id"] = user_auth[0].id

    return {"access_token": access_security.create_access_token(subject=user),
            "refresh_token": refresh_security.create_refresh_token(subject=user)}


@router.post("/token/refresh", response_model=TokenReturn)
async def obtain_refresh_token(credentials: JAC = Security(refresh_security)):
    access_token = access_security.create_access_token(subject=credentials.subject)
    refresh_token = refresh_security.create_refresh_token(subject=credentials.subject)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.get("/users/me", responses={200: {"model": RegistrationReturn}})
async def get_account(session: Session = Depends(get_session),
                      credentials: JAC = Security(access_security)):
    user = await get_user_by_id(session=session, user_id=credentials["id"])
    return {"response": user.first()[0].get_security_fields()}
