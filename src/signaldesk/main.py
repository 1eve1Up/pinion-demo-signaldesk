from contextlib import asynccontextmanager

from fastapi import FastAPI

from signaldesk.db import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await dispose_engine()


app = FastAPI(title="SignalDesk API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
