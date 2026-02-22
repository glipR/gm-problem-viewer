from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/health", tags=["health"])
def health():
    """Service liveness check."""
    return {"status": "ok"}
