import datetime
import random
import uuid

from fastapi import APIRouter, Depends, Security, Form

from jwt_securities import refresh_security, access_security, JAC
from libraries.email_handler import send_email
from routers.authorization.pydantic_models import Registration, Credentials, RegistrationReturn, TokenReturn, \
    DefaultError, RecentFields, ResetPassword, DefaultOk
from routers.authorization.responses import Responses
from routers.authorization.service import Service
from routers.authorization.utils import generate_recent_url
from routers.authorization.validators import registration_validate, authorization_validate

router = APIRouter()


@router.post("/registration/", responses={200: {"model": RegistrationReturn}, 400: {"model": DefaultError}})
async def registration(user: dict = Depends(Registration.as_form),
                       service: Service = Depends(Service)):
    await registration_validate(user, service)
    new_user = await service.create_user(user)

    return new_user


@router.post("/token/", responses={401: {"model": DefaultError}, 200: {"model": TokenReturn}})
async def obtain_token(user: dict = Depends(Credentials.as_form), service: Service = Depends(Service)):
    user_instance = await authorization_validate(user, service)

    del user["password"]
    user["id"] = str(user_instance.id)

    await service.set_auth(user["email"])

    return await access_security.create_return(user)


@router.post("/token/refresh", responses={401: {"model": DefaultError}, 200: {"model": TokenReturn}})
async def obtain_refresh_token(service: Service = Depends(Service), credentials: JAC = Security(refresh_security)):
    await service.set_auth(credentials.subject["email"])

    return await refresh_security.create_return(credentials.subject)


@router.get("/users/me", responses={200: {"model": RegistrationReturn}})
async def get_account(service: Service = Depends(Service), credentials: JAC = Security(access_security)):
    instance = await service.get_user_by_id(credentials["id"])

    return instance.get_security_fields()


@router.post("/recent", responses={200: {"model": DefaultOk}, 400: {"model": DefaultError}})
async def recent_password(service: Service = Depends(Service), recent: RecentFields = Depends(RecentFields.as_form)):
    data = {"token": str(uuid.uuid4()),
            "key": str(random.randint(100000, 999999)),
            "expired_at": datetime.datetime.now() + datetime.timedelta(hours=2)}

    await service.create_recent(recent["email"], data)
    url = generate_recent_url(data)
    send_email(email=recent["email"], text=url)

    return {"status": Responses.DEFAULT_OK}


@router.post("/recent/{uuid}/{key}", responses={200: {"model": DefaultOk}, 400: {"model": DefaultError}})
async def set_recent_password(recent_uuid: str, key: str, password: str = Form(...),
                              service: Service = Depends(Service)):
    await service.check_recent(recent_uuid, key, password)
    return {"status": Responses.DEFAULT_OK}


@router.post("/reset/password/", responses={200: {"model": DefaultOk}, 400: {"model": DefaultError}})
async def reset_password(reset: ResetPassword = Depends(ResetPassword.as_form),
                         service: Service = Depends(Service), credentials: JAC = Security(access_security)):
    await service.check_reset(reset["old_password"], reset["new_password"], credentials["email"])
    return {"status": Responses.DEFAULT_OK}
