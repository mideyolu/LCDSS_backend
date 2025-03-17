from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, async_session, engine
from routes import route
from contextlib import asynccontextmanager
from log import delete_old_logs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from model_loader import load_model  # ✅ Updated import


async def close_db_connections():
    """Closes all database connections gracefully."""
    await engine.dispose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown logic."""
    await init_db()
    await load_model()  # ✅ Load model once (optimized)
    print("Application startup: Database and Model initialized")

    scheduler = AsyncIOScheduler()

    @scheduler.scheduled_job("interval", hours=1)
    async def cleanup_logs():
        print("Running scheduled log cleanup...")
        async with async_session() as session:
            deleted_count = await delete_old_logs(session)

    scheduler.start()
    await cleanup_logs()  # Initial cleanup

    try:
        yield
    finally:
        await close_db_connections()
        scheduler.shutdown()
        print("Application shutdown: Database connections closed")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(route.router, tags=["Authentication"], prefix="/auth")
