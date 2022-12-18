import os

from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearerCookie

access_security = JwtAccessBearerCookie(secret_key=os.getenv("ACCESS_KEY"), auto_error=True)
refresh_security = JwtRefreshBearerCookie(secret_key=os.getenv("ACCESS_KEY"), auto_error=True)
