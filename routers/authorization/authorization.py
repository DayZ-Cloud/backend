import datetime
import random
import re
import uuid

from fastapi import APIRouter, Depends, Security, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession as Session
from starlette.responses import JSONResponse

from database import get_session
from jwt_securities import refresh_security, access_security, JAC
from libraries.email_handler import send_email
from routers.authorization import service
from routers.authorization.pydantic_models import Registration, Credentials, RegistrationReturn, TokenReturn, \
    RegistrationError, RecentFields
from routers.authorization.responses import Responses
from routers.authorization.service import check_password, get_user_by_id, create_recent, check_recent, check_reset, \
    set_auth, check_user_exists

router = APIRouter()


async def user_exists(user: Registration = Depends(Registration.as_form), db: Session = Depends(get_session)):
    user = await check_user_exists(db, user["email"])

    if user.scalar():
        raise HTTPException(status_code=400, detail="This email already exists")


async def valid_fields(user: Registration = Depends(Registration.as_form)):
    if not re.match(r"^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$", user["email"]):
        raise HTTPException(status_code=400, detail="Not a valid email address")

    if len(user["password"]) < 7 or len(user["password"]) > 32:
        raise HTTPException(status_code=400, detail="Password length must be between 7 or 32")


@router.post("/registration/", responses={200: {"model": RegistrationReturn}, 400: {"model": RegistrationError}},
             dependencies=[Depends(valid_fields), Depends(user_exists)])
async def registration(user: Registration = Depends(Registration.as_form),
                       db: Session = Depends(get_session)):
    user["password"] = await service.create_password(password=user["password"])
    new_user = await service.create_user(db, user)

    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token/", response_model=TokenReturn)
async def obtain_token(user: Credentials = Depends(Credentials.as_form),
                       db: Session = Depends(get_session)):
    if (user_auth := await check_password(db, user["password"], user["email"])) is None:
        return JSONResponse(status_code=401, content={"detail": "This email or password not found."})

    del user["password"]
    user["id"] = user_auth[0].id

    await set_auth(db, user["email"])

    return await access_security.create_return(user)


@router.post("/token/refresh", response_model=TokenReturn)
async def obtain_refresh_token(db: Session = Depends(get_session), credentials: JAC = Security(refresh_security)):
    await set_auth(db, credentials.subject["email"])

    return await refresh_security.create_return(credentials.subject)


@router.get("/users/me", responses={200: {"model": RegistrationReturn}})
async def get_account(db: Session = Depends(get_session), credentials: JAC = Security(access_security)):
    user = await get_user_by_id(session=db, user_id=credentials["id"])
    return {"response": user.first()[0].get_security_fields()}


def generate_recent_url(data: dict) -> str:
    return f"https://hotlinetrade.страж.shop/api/v1/recent/{data['token']}/{data['key']}/"


@router.post("/recent")
async def recent_password(db: Session = Depends(get_session), recent: RecentFields = Depends(RecentFields.as_form)):
    data = {"token": str(uuid.uuid4()),
            "key": str(random.randint(100000, 999999)),
            "expired_at": datetime.datetime.now() + datetime.timedelta(hours=2)}

    await create_recent(db, recent.email, data)
    url = generate_recent_url(data)
    send_email(email=recent.email, text=url)
    await db.commit()
    return Responses.DEFAULT_OK


@router.post("/recent/{uuid}/{key}")
async def set_new_password(uuid: str, key: str, password: str = Form(...), db: Session = Depends(get_session)):
    await check_recent(db, uuid, key, password)
    return Responses.DEFAULT_OK


@router.post("/reset/password/")
async def reset_password(old_password: str = Form(...), new_password: str = Form(),
                         db: Session = Depends(get_session), credentials: JAC = Security(access_security)):
    await check_reset(db, old_password, new_password, credentials["email"])
    return Responses.DEFAULT_OK
