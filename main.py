from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from database import engine, base
from routers.authorization import authorization
from routers.banners import banners
from routers.news import news
from routers.stats import stats
from routers.servers import servers

app = FastAPI()

router = APIRouter(prefix="/api/v1")
admin_panel_router = APIRouter(prefix="/apanel")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])


@router.on_event("startup")
async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


admin_panel_router.include_router(stats.router)
router.include_router(admin_panel_router)
router.include_router(news.router)
router.include_router(banners.router)
router.include_router(authorization.router)
router.include_router(servers.router)
app.include_router(router)
