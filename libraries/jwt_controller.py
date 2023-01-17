import datetime
import os
from typing import Dict, Any
from uuid import uuid4

from fastapi import Security, Header, HTTPException, Depends
from fastapi.security import HTTPBearer
from jose import jwt
from starlette.status import HTTP_401_UNAUTHORIZED

from routers.authorization.service import Service


class JWTController:
    async def create_token(self, subject: dict, target: str):
        match target:
            case "refresh":
                timedelta = {"days": 31}

            case "access":
                timedelta = {"minutes": 15}

            case _:
                timedelta = {"days": 1}
        expire = datetime.timedelta(**timedelta)
        to_encode = await self._generate_payload(subject, expire, str(uuid4()), target)
        encoded_jwt = jwt.encode(to_encode, os.getenv("ACCESS_KEY"))
        return encoded_jwt

    async def create_return(self, subject):
        access = await self.create_token(subject, "access")
        refresh = await self.create_token(subject, "refresh")
        return {"access_token": access, "refresh_token": refresh}

    async def _generate_payload(self,
                                subject: Dict[str, Any],
                                expires_delta: datetime.timedelta,
                                unique_identifier: str,
                                token_type: str,
                                ) -> Dict[str, Any]:

        now = datetime.datetime.utcnow()

        return {
            "subject": subject.copy(),  # main subject
            "type": token_type,  # 'access' or 'refresh' token
            "exp": now + expires_delta,  # expire time
            "iat": now,  # creation time
            "jti": unique_identifier,  # uuid
        }


class JwtBearer(HTTPBearer):
    def __init__(self, *args: Any, **kwargs: Any):
        HTTPBearer.__init__(self, *args, auto_error=False, **kwargs)


class Credentials:
    def __init__(self, subject: Dict[str, Any], jti: str | None = None):
        self.subject = subject
        self.jti = jti

    def __getitem__(self, item: str) -> Any:
        return self.subject[item]


class DefaultVerifier:
    async def _get_payload(self, token: str | None) -> Dict[str, Any] | None:

        if not token:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Credentials are not provided"
            )

        # Try to decode jwt token. auto_error on error
        payload = await self._decode(token)
        return payload

    async def _get_credentials(self, token, payload_type):
        payload = await self._get_payload(token)
        if payload is None:
            return None

        if "type" not in payload or payload["type"] != payload_type:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Wrong token: 'type' is not '{payload_type}'",
            )

        return Credentials(payload["subject"], payload.get("jti", None))

    async def _decode(self, token: str) -> Dict[str, Any] | None:
        try:
            payload: Dict[str, Any] = jwt.decode(
                token,
                os.getenv("ACCESS_KEY"),
                algorithms=["HS256"],
                options={"leeway": 10},
            )
            return payload
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail=f"Token time expired: {e}"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail=f"Wrong token: {e}"
            )


class AccessVerifier(DefaultVerifier, JWTController):
    async def __call__(self, _bearer: JwtBearer = Security(JwtBearer()), service: Service = Depends(Service)):
        if _bearer is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Credentials are not provided.")

        user = await self._get_credentials(_bearer.credentials, "access")

        if await service.check_user_exists(user_id=user["id"]):
            return user

        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not exists")


class RefreshVerifier(DefaultVerifier, JWTController):
    async def __call__(self, x_refresh_token: str | None = Header(None), service: Service = Depends(Service)):

        if x_refresh_token is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                                detail="Credentials are not provided. Insert into header key 'X-Refresh-Token'")

        user = await self._get_credentials(x_refresh_token, "refresh")

        if not await service.check_user_exists(user_id=user["id"]):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not exists")

        return user

