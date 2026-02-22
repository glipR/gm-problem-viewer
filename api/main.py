from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import problems, solutions, validators, tests, export, jobs, statement, review

app = FastAPI(
    title="GM Problem Viewer",
    description="API for managing and testing competitive programming problems.",
    version="0.1.0",
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
app.include_router(jobs.router)


@app.get("/health", tags=["health"])
def health():
    """Service liveness check."""
    return {"status": "ok"}
