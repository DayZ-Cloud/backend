import datetime
import os
from typing import Dict, Any
from uuid import uuid4

from fastapi import Security, Header, HTTPException
from fastapi.security import HTTPBearer
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearerCookie
from jose import jwt
from jose.exceptions import JWKError
from starlette.status import HTTP_401_UNAUTHORIZED


# access_security = JwtAccessBearerCookie(secret_key=os.getenv("ACCESS_KEY"), auto_error=True)
# refresh_security = JwtRefreshBearerCookie(secret_key=os.getenv("ACCESS_KEY"), auto_error=True)


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

    async def _get_credentials(self, token, type):
        payload = await self._get_payload(token)

        if payload is None:
            return None

        if "type" not in payload or payload["type"] != type:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Wrong token: 'type' is not '{type}'",
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
    async def __call__(self, _bearer: JwtBearer = Security(JwtBearer())):
        if _bearer is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                                detail="Credentials are not provided.")
        return await self._get_credentials(_bearer.credentials, "access")


class RefreshVerifier(DefaultVerifier, JWTController):
    async def __call__(self, x_refresh_token: str | None = Header(None)):
        if x_refresh_token is None:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
                                detail="Credentials are not provided. Insert into header key 'X-Refresh-Token'")
        return await self._get_credentials(x_refresh_token, "refresh")

