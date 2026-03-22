from contextlib import asynccontextmanager

from fastapi import FastAPI

from signaldesk.api.auth import router as auth_router
from signaldesk.api.contacts import router as contacts_router
from signaldesk.db import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_engine()


app = FastAPI(title="SignalDesk API", version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(contacts_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
