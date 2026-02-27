import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.jobs import purge_stale_jobs
from api.routes import problems, solutions, validators, tests, export, jobs, statement, review, todo, editorial

logger = logging.getLogger(__name__)

_PURGE_INTERVAL = 5 * 60  # seconds


async def _periodic_purge() -> None:
    while True:
        await asyncio.sleep(_PURGE_INTERVAL)
        try:
            deleted = purge_stale_jobs()
            if deleted:
                logger.info("Job cache purge: removed %d stale file(s)", deleted)
        except Exception:
            logger.exception("Job cache purge failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_periodic_purge())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="GM Problem Viewer",
    description="API for managing and testing competitive programming problems.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(problems.router)
app.include_router(solutions.router)
app.include_router(validators.router)
app.include_router(tests.router)
app.include_router(export.router)
app.include_router(statement.router)
app.include_router(review.router)
app.include_router(todo.router)
app.include_router(editorial.router)
app.include_router(jobs.router)


@app.get("/health", tags=["health"])
def health():
    """Service liveness check."""
    return {"status": "ok"}
