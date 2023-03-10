import datetime

from pydantic import BaseModel

from depends import as_form


@as_form
class Registration(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str


@as_form
class Credentials(BaseModel):
    email: str
    password: str


@as_form
class ResetPassword(BaseModel):
    old_password: str
    new_password: str


class RegistrationReturn(BaseModel):
    avatar: None
    id: int
    created: datetime.datetime
    email: str
    first_name: str
    last_name: str
    last_auth: None


@as_form
class RecentFields(BaseModel):
    email: str


class TokenReturn(BaseModel):
    access_token: str
    refresh_token: str


class DefaultError(BaseModel):
    detail: str


class DefaultOk(BaseModel):
    status: str
