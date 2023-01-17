import asyncio

from fastapi import FastAPI, APIRouter, Depends, Header, Query
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

from database import engine, base
from libraries.jwt_controller import AccessVerifier
from routers.authorization import authorization
from routers.banners import banners
from routers.news import news
from routers.servers.service import Service
from routers.stats import stats
from routers.servers import servers


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


app = FastAPI(title="DayZ Cloud API",
              version='1.2.4',
              on_startup=[create_database])

router = APIRouter(prefix="/api/v1")
admin_panel_router = APIRouter(prefix="/apanel")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])


@app.websocket("/ws/server/info")
async def server_info_socker(websocket: WebSocket,
                             authorization: str = Header(None),
                             service: Service = Depends(Service),
                             server_uuid: str = Query(None)):
    await websocket.accept()
    if not authorization:
        return await websocket.close(code=1002, reason="Not credentials provided")

    if not server_uuid:
        return await websocket.close(code=1002, reason="server_uuid not may be null")

    if len(authorization.split()) != 2:
        return await websocket.close(code=1002, reason="Broken token")

    user = await AccessVerifier()._get_credentials(authorization.split()[1], "access")
    server = await service.get_server_by_uuid(user=user["id"], server_uuid=server_uuid)

    try:
        while True:
            await websocket.send_json(server.get_security_fields())
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        return

admin_panel_router.include_router(stats.router)
router.include_router(admin_panel_router)
router.include_router(news.router)
router.include_router(banners.router)
router.include_router(authorization.router)
router.include_router(servers.router)
app.include_router(router)
