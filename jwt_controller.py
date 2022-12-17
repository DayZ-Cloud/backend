import os

from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearer

access_security = JwtAccessBearerCookie(secret_key=os.getenv("ACCESS_KEY"), auto_error=True)
refresh_security = JwtRefreshBearer(secret_key="secret_key", auto_error=True)
