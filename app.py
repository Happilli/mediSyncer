from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting mediSyncer")
    print("Database schema managed by alembic")
    print("run-> alembic upgrade head")
    yield
    print("Shutting down mediSyncer")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="mediSyncer",
    description="Hospital, patient, doctor everything medical management stuff",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore


@app.get("/")
@limiter.limit("5/minutes")
async def root(request: Request):
    return {"status": "mediSyncer online"}
