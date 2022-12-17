import re

from fastapi import APIRouter, Depends, Security, HTTPException
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


async def user_exists(user: Registration = Depends(Registration.as_form), db: Session = Depends(get_session)):
    user = await get_user_by_email(db, user.email)
    if user.all():
        raise HTTPException(status_code=400, detail="This email already exists")


async def valid_fields(user: Registration = Depends(Registration.as_form)):
    if not re.match(r"^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$", user.email):
        raise HTTPException(status_code=400, detail="Not a valid email address")

    if len(user["password"]) < 7 or len(user["password"]) > 32:
        raise HTTPException(status_code=400, detail="Password length must be between 7 or 32")


@router.post("/registration/", responses={200: {"model": RegistrationReturn}, 400: {"model": RegistrationError}},
             dependencies=[Depends(valid_fields), Depends(user_exists)])
async def registration(user: Registration = Depends(Registration.as_form),
                       db: Session = Depends(get_session)):
    user = user.__dict__

    user["password"] = await service.create_password(password=user["password"])
    new_user = await service.create_user(db, user)

    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token/", response_model=TokenReturn)
async def obtain_token(credentials: Credentials = Depends(Credentials.as_form),
                       db: Session = Depends(get_session)):
    user = credentials.__dict__
    if (user_auth := await check_password(db, user["password"], user["email"])) is None:
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
async def get_account(db: Session = Depends(get_session),
                      credentials: JAC = Security(access_security)):
    user = await get_user_by_id(session=db, user_id=credentials["id"])
    return {"response": user.first()[0].get_security_fields()}
