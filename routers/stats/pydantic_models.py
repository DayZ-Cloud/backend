from pydantic import BaseModel


class GetUsersCount(BaseModel):
    users_count: int


class GetServersCount(BaseModel):
    servers_count: int
